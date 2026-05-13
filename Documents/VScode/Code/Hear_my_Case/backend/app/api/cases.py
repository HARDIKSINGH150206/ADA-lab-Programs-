"""Case management API routes"""
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.db.database import get_db
from app.models.case import Case, CaseType, CaseStatus, CaseStep
from app.models.evidence import Evidence
from app.models.notification import Notification
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.cases import (
    CaseResponse,
    CaseListResponse,
    CaseStepResponse,
    CreateCaseRequest,
    UpdateCaseRequest,
)
from app.services.ai import generate_case_analysis
from app.services.storage import delete_stored_file

router = APIRouter(prefix="/api/cases", tags=["cases"])
logger = logging.getLogger(__name__)


def _parse_uuid(case_id: str) -> UUID:
    """Parse and validate UUID"""
    try:
        return UUID(case_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid case id",
        ) from exc


async def _get_case_by_id(db: AsyncSession, case_id: str, user_id: str = None) -> Case:
    """Get case by ID with optional user ownership check"""
    case_uuid = _parse_uuid(case_id)
    stmt = select(Case).where(Case.id == case_uuid)
    result = await db.execute(stmt)
    case = result.scalars().first()
    
    if not case:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    # Check ownership if user_id provided
    if user_id and str(case.user_id) != user_id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this case",
        )
    
    return case


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=CaseResponse, status_code=http_status.HTTP_201_CREATED)
async def create_case(
    request: CreateCaseRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new case for the current user"""
    user_id = UUID(current_user["sub"])
    
    new_case = Case(
        user_id=user_id,
        case_type=CaseType(request.case_type),
        status=CaseStatus.DRAFT,
        employer_name=request.employer_name,
        amount_owed=request.amount_owed,
        period_start=request.period_start,
        period_end=request.period_end,
        contract_type=request.contract_type,
    )
    
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    default_steps = [
        CaseStep(
            case_id=new_case.id,
            step_number="1",
            title="Review case details",
            description="Confirm the core facts, dates, and parties involved.",
            status="pending",
        ),
        CaseStep(
            case_id=new_case.id,
            step_number="2",
            title="Upload supporting evidence",
            description="Collect pay slips, chats, notices, and other supporting files.",
            status="pending",
        ),
        CaseStep(
            case_id=new_case.id,
            step_number="3",
            title="Generate legal guidance",
            description="Run the case through AI analysis to produce next steps.",
            status="pending",
        ),
    ]
    db.add_all(default_steps)
    await db.commit()
    
    logger.info(f"Case created: {new_case.id} for user {user_id}")
    return CaseResponse.model_validate(new_case)


@router.get("", response_model=CaseListResponse)
async def list_cases(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    case_type: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
):
    """List all cases for the current user with filters"""
    user_id = UUID(current_user["sub"])
    
    filters = [Case.user_id == user_id]
    
    if case_type:
        try:
            filters.append(Case.case_type == CaseType(case_type))
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid case type: {case_type}",
            )
    
    if status:
        try:
            filters.append(Case.status == CaseStatus(status))
        except ValueError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}",
            )
    
    if search:
        search_term = f"%{search}%"
        filters.append(Case.employer_name.ilike(search_term))
    
    # Count total
    count_stmt = select(func.count()).select_from(Case).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()
    
    # Fetch paginated results
    stmt = (
        select(Case)
        .where(*filters)
        .order_by(Case.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    return CaseListResponse(
        items=[CaseResponse.model_validate(case) for case in cases],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific case by ID"""
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    return CaseResponse.model_validate(case)


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    request: UpdateCaseRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a case"""
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    
    # Apply updates
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(case, field, value)
    
    await db.commit()
    await db.refresh(case)
    
    logger.info(f"Case updated: {case.id}")
    return CaseResponse.model_validate(case)


@router.delete("/{case_id}", response_model=MessageResponse)
async def delete_case(
    case_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a case and its related records"""
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    
    evidence_result = await db.execute(select(Evidence).where(Evidence.case_id == case.id))
    for evidence in evidence_result.scalars().all():
        delete_stored_file(evidence.file_url)
        await db.delete(evidence)

    steps_result = await db.execute(select(CaseStep).where(CaseStep.case_id == case.id))
    for step in steps_result.scalars().all():
        await db.delete(step)

    notifications_result = await db.execute(select(Notification).where(Notification.related_case_id == case.id))
    for notification in notifications_result.scalars().all():
        await db.delete(notification)

    await db.delete(case)
    await db.commit()
    
    logger.info(f"Case deleted: {case.id}")
    return MessageResponse(
        success=True,
        message="Case deleted successfully",
    )


# ==================== AI ANALYSIS ====================

@router.post("/{case_id}/analyze", response_model=CaseResponse)
async def analyze_case(
    case_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered case analysis using Claude API
    Populates: case_summary, applicable_laws, what_should_happen, next_steps
    """
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    
    # Generate analysis
    evidence_count_stmt = select(func.count()).select_from(Evidence).where(Evidence.case_id == case.id)
    evidence_count = (await db.execute(evidence_count_stmt)).scalar_one()

    analysis = await generate_case_analysis(
        {
            "case_type": case.case_type.value,
            "employer_name": case.employer_name,
            "amount_owed": case.amount_owed,
            "period_start": case.period_start,
            "period_end": case.period_end,
            "contract_type": case.contract_type,
            "evidence_count": evidence_count,
        }
    )
    
    # Update case with analysis
    if analysis:
        case.case_summary = analysis.get("case_summary")
        case.applicable_laws = analysis.get("applicable_laws")
        case.what_should_happen = analysis.get("what_should_happen")
        case.next_steps = analysis.get("next_steps")
        case.status = CaseStatus.REPORT_GENERATED
        
        await db.commit()
        await db.refresh(case)
        
        logger.info(f"Case analysis generated: {case.id}")
    else:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate case analysis",
        )
    
    return CaseResponse.model_validate(case)


# ==================== CASE STEPS ====================

@router.get("/{case_id}/steps", response_model=list[CaseStepResponse])
async def get_case_steps(
    case_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all steps for a case"""
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    
    stmt = select(CaseStep).where(CaseStep.case_id == case.id).order_by(CaseStep.step_number)
    result = await db.execute(stmt)
    steps = result.scalars().all()
    
    return [CaseStepResponse.model_validate(step) for step in steps]


@router.patch("/{case_id}/steps/{step_id}", response_model=MessageResponse)
async def update_case_step(
    case_id: str,
    step_id: str,
    status: str = Query(..., regex="^(pending|in_progress|completed)$"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the status of a case step"""
    case = await _get_case_by_id(db, case_id, current_user["sub"])
    
    step_uuid = _parse_uuid(step_id)
    stmt = select(CaseStep).where(
        CaseStep.id == step_uuid,
        CaseStep.case_id == case.id,
    )
    result = await db.execute(stmt)
    step = result.scalars().first()
    
    if not step:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Step not found",
        )
    
    step.status = status
    await db.commit()
    
    logger.info(f"Case step updated: {step.id} -> {status}")
    return MessageResponse(
        success=True,
        message=f"Step status updated to {status}",
    )
