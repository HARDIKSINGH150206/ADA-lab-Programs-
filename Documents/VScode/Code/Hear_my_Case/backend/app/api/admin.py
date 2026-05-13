"""Admin CRUD routes for groups, lawyers, and NGOs"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.db.database import get_db
from app.models.case import Case
from app.models.group import Group
from app.models.lawyer import Lawyer
from app.models.ngo import NGO
from app.models.notification import Notification
from app.models.user import UserRole
from app.schemas.auth import MessageResponse
from app.schemas.resources import (
    GroupCreateRequest,
    GroupResponse,
    GroupUpdateRequest,
    LawyerCreateRequest,
    LawyerResponse,
    LawyerUpdateRequest,
    NGOCreateRequest,
    NGOResponse,
    NGOUpdateRequest,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") in {UserRole.NGO_ADMIN.value, UserRole.SUPER_ADMIN.value}


def _require_admin(current_user: dict) -> None:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def _parse_uuid(value: str, label: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {label}") from exc


async def _fetch_or_404(db: AsyncSession, model, object_id: str, label: str):
    stmt = select(model).where(model.id == _parse_uuid(object_id, label))
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label.title()} not found")
    return item


def _apply_updates(model_obj, payload) -> None:
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None and hasattr(model_obj, field):
            setattr(model_obj, field, value)


@router.get("/groups", response_model=list[GroupResponse])
async def list_groups(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    _require_admin(current_user)
    stmt = select(Group).order_by(Group.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [GroupResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: GroupCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    group = Group(
        state=request.state,
        case_type=request.case_type,
        notice_status=request.notice_status,
        assigned_lawyer_id=_parse_uuid(request.assigned_lawyer_id, "lawyer id") if request.assigned_lawyer_id else None,
        member_count=request.member_count,
        notice_url=request.notice_url,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return GroupResponse.model_validate(group)


@router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    group = await _fetch_or_404(db, Group, group_id, "group")
    return GroupResponse.model_validate(group)


@router.patch("/groups/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    request: GroupUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    group = await _fetch_or_404(db, Group, group_id, "group")
    _apply_updates(
        group,
        request,
    )
    if request.assigned_lawyer_id is not None:
        group.assigned_lawyer_id = _parse_uuid(request.assigned_lawyer_id, "lawyer id")
    await db.commit()
    await db.refresh(group)
    return GroupResponse.model_validate(group)


@router.delete("/groups/{group_id}", response_model=MessageResponse)
async def delete_group(
    group_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    group = await _fetch_or_404(db, Group, group_id, "group")
    await db.execute(update(Case).where(Case.group_id == group.id).values(group_id=None))
    await db.execute(
        update(Notification).where(Notification.related_group_id == group.id).values(related_group_id=None)
    )
    await db.delete(group)
    await db.commit()
    return MessageResponse(success=True, message="Group deleted successfully")


@router.get("/lawyers", response_model=list[LawyerResponse])
async def list_lawyers(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    _require_admin(current_user)
    stmt = select(Lawyer).order_by(Lawyer.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [LawyerResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/lawyers", response_model=LawyerResponse, status_code=status.HTTP_201_CREATED)
async def create_lawyer(
    request: LawyerCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    if request.email:
        stmt = select(Lawyer).where(Lawyer.email == request.email)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    stmt = select(Lawyer).where(Lawyer.phone_number == request.phone_number)
    if (await db.execute(stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already in use")
    if request.bar_council_id:
        stmt = select(Lawyer).where(Lawyer.bar_council_id == request.bar_council_id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bar council id already in use")
    lawyer = Lawyer(
        user_id=_parse_uuid(request.user_id, "user id"),
        full_name=request.full_name,
        phone_number=request.phone_number,
        email=request.email,
        bio=request.bio,
        profile_picture_url=request.profile_picture_url,
        years_of_experience=request.years_of_experience,
        specializations=request.specializations,
        bar_council_id=request.bar_council_id,
        is_available=request.is_available,
        available_for_group_cases=request.available_for_group_cases,
        states_served=request.states_served,
        average_rating=request.average_rating,
        total_cases=request.total_cases,
        active_cases=request.active_cases,
        office_address=request.office_address,
        languages=request.languages,
    )
    db.add(lawyer)
    await db.commit()
    await db.refresh(lawyer)
    return LawyerResponse.model_validate(lawyer)


@router.get("/lawyers/{lawyer_id}", response_model=LawyerResponse)
async def get_lawyer(
    lawyer_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    lawyer = await _fetch_or_404(db, Lawyer, lawyer_id, "lawyer")
    return LawyerResponse.model_validate(lawyer)


@router.patch("/lawyers/{lawyer_id}", response_model=LawyerResponse)
async def update_lawyer(
    lawyer_id: str,
    request: LawyerUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    lawyer = await _fetch_or_404(db, Lawyer, lawyer_id, "lawyer")
    if request.email and request.email != lawyer.email:
        stmt = select(Lawyer).where(Lawyer.email == request.email, Lawyer.id != lawyer.id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    if request.phone_number and request.phone_number != lawyer.phone_number:
        stmt = select(Lawyer).where(Lawyer.phone_number == request.phone_number, Lawyer.id != lawyer.id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already in use")
    if request.bar_council_id and request.bar_council_id != lawyer.bar_council_id:
        stmt = select(Lawyer).where(Lawyer.bar_council_id == request.bar_council_id, Lawyer.id != lawyer.id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bar council id already in use")
    _apply_updates(lawyer, request)
    if request.user_id is not None:
        lawyer.user_id = _parse_uuid(request.user_id, "user id")
    await db.commit()
    await db.refresh(lawyer)
    return LawyerResponse.model_validate(lawyer)


@router.delete("/lawyers/{lawyer_id}", response_model=MessageResponse)
async def delete_lawyer(
    lawyer_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    lawyer = await _fetch_or_404(db, Lawyer, lawyer_id, "lawyer")
    await db.execute(update(Case).where(Case.lawyer_id == lawyer.id).values(lawyer_id=None))
    await db.execute(update(Group).where(Group.assigned_lawyer_id == lawyer.id).values(assigned_lawyer_id=None))
    await db.delete(lawyer)
    await db.commit()
    return MessageResponse(success=True, message="Lawyer deleted successfully")


@router.get("/ngos", response_model=list[NGOResponse])
async def list_ngos(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    _require_admin(current_user)
    stmt = select(NGO).order_by(NGO.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [NGOResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/ngos", response_model=NGOResponse, status_code=status.HTTP_201_CREATED)
async def create_ngo(
    request: NGOCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    stmt = select(NGO).where(NGO.name == request.name)
    if (await db.execute(stmt)).scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NGO name already in use")
    if request.email:
        stmt = select(NGO).where(NGO.email == request.email)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    ngo = NGO(
        name=request.name,
        email=request.email,
        phone_number=request.phone_number,
        description=request.description,
        logo_url=request.logo_url,
        website=request.website,
        states_served=request.states_served,
        case_types_handled=request.case_types_handled,
        is_active=request.is_active,
        contact_person_name=request.contact_person_name,
        contact_person_phone=request.contact_person_phone,
        average_rating=request.average_rating,
        total_cases_handled=request.total_cases_handled,
    )
    db.add(ngo)
    await db.commit()
    await db.refresh(ngo)
    return NGOResponse.model_validate(ngo)


@router.get("/ngos/{ngo_id}", response_model=NGOResponse)
async def get_ngo(
    ngo_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    ngo = await _fetch_or_404(db, NGO, ngo_id, "ngo")
    return NGOResponse.model_validate(ngo)


@router.patch("/ngos/{ngo_id}", response_model=NGOResponse)
async def update_ngo(
    ngo_id: str,
    request: NGOUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    ngo = await _fetch_or_404(db, NGO, ngo_id, "ngo")
    if request.name and request.name != ngo.name:
        stmt = select(NGO).where(NGO.name == request.name, NGO.id != ngo.id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NGO name already in use")
    if request.email and request.email != ngo.email:
        stmt = select(NGO).where(NGO.email == request.email, NGO.id != ngo.id)
        if (await db.execute(stmt)).scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    _apply_updates(ngo, request)
    await db.commit()
    await db.refresh(ngo)
    return NGOResponse.model_validate(ngo)


@router.delete("/ngos/{ngo_id}", response_model=MessageResponse)
async def delete_ngo(
    ngo_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(current_user)
    ngo = await _fetch_or_404(db, NGO, ngo_id, "ngo")
    await db.delete(ngo)
    await db.commit()
    return MessageResponse(success=True, message="NGO deleted successfully")
