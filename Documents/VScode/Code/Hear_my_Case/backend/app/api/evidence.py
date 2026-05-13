"""Evidence upload and management routes"""
from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.config import settings
from app.db.database import get_db
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.user import UserRole
from app.schemas.evidence import (
    EvidenceListResponse,
    EvidenceMetadataResponse,
    EvidenceResponse,
    EvidenceUpdateRequest,
)
from app.services.evidence import store_evidence_file
from app.services.storage import delete_stored_file

router = APIRouter(prefix="/api", tags=["evidence"])
logger = logging.getLogger(__name__)


def _parse_uuid(value: str, label: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {label}") from exc


async def _get_case_or_404(db: AsyncSession, case_id: str) -> Case:
    stmt = select(Case).where(Case.id == _parse_uuid(case_id, "case id"))
    result = await db.execute(stmt)
    case = result.scalars().first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


async def _ensure_case_access(case: Case, current_user: dict) -> None:
    if str(case.user_id) == current_user["sub"]:
        return
    if current_user.get("role") in {UserRole.NGO_ADMIN.value, UserRole.SUPER_ADMIN.value, UserRole.LAWYER.value}:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this case")


async def _get_evidence_or_404(db: AsyncSession, evidence_id: str) -> Evidence:
    stmt = select(Evidence).where(Evidence.id == _parse_uuid(evidence_id, "evidence id"))
    result = await db.execute(stmt)
    evidence = result.scalars().first()
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    return evidence


@router.post("/cases/{case_id}/evidence", response_model=EvidenceMetadataResponse, status_code=status.HTTP_201_CREATED)
async def upload_case_evidence(
    case_id: str,
    file: UploadFile = File(...),
    user_description: str | None = Form(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an evidence file for a case."""
    case = await _get_case_or_404(db, case_id)
    await _ensure_case_access(case, current_user)

    try:
        upload_result = await store_evidence_file(file, max_size_bytes=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        ) from exc

    evidence = Evidence(
        case_id=case.id,
        file_name=file.filename or "upload.bin",
        file_url=upload_result.file_url,
        file_size=str(upload_result.file_size),
        mime_type=file.content_type,
        category=upload_result.category,
        confidence_score=str(upload_result.confidence_score),
        auto_tags=upload_result.tags,
        extracted_text=upload_result.extracted_text or None,
        ai_summary=upload_result.ai_summary or None,
        user_description=user_description,
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)

    logger.info("Evidence uploaded: %s for case %s", evidence.id, case.id)
    return EvidenceMetadataResponse(
        evidence=EvidenceResponse.model_validate(evidence),
        extracted_text=evidence.extracted_text,
        auto_tags=upload_result.tags,
        ai_summary=evidence.ai_summary,
    )


@router.get("/cases/{case_id}/evidence", response_model=EvidenceListResponse)
async def list_case_evidence(
    case_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List evidence for a case."""
    case = await _get_case_or_404(db, case_id)
    await _ensure_case_access(case, current_user)

    count_stmt = select(func.count()).select_from(Evidence).where(Evidence.case_id == case.id)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(Evidence)
        .where(Evidence.case_id == case.id)
        .order_by(Evidence.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    return EvidenceListResponse(
        items=[EvidenceResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get evidence metadata."""
    evidence = await _get_evidence_or_404(db, evidence_id)
    case = await _get_case_or_404(db, str(evidence.case_id))
    await _ensure_case_access(case, current_user)
    return EvidenceResponse.model_validate(evidence)


@router.patch("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: str,
    request: EvidenceUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update evidence metadata."""
    evidence = await _get_evidence_or_404(db, evidence_id)
    case = await _get_case_or_404(db, str(evidence.case_id))
    await _ensure_case_access(case, current_user)

    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None and hasattr(evidence, field):
            setattr(evidence, field, value)

    await db.commit()
    await db.refresh(evidence)
    return EvidenceResponse.model_validate(evidence)


@router.delete("/evidence/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete evidence and remove stored file."""
    evidence = await _get_evidence_or_404(db, evidence_id)
    case = await _get_case_or_404(db, str(evidence.case_id))
    await _ensure_case_access(case, current_user)

    file_url = evidence.file_url
    await db.delete(evidence)
    await db.commit()
    delete_stored_file(file_url)

    return {"success": True, "message": "Evidence deleted successfully"}
