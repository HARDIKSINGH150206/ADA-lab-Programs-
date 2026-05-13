"""User management API routes"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import MessageResponse, UserResponse
from app.schemas.users import (
    UserAdminUpdateRequest,
    UserListResponse,
    UserProfileUpdateRequest,
)

router = APIRouter(prefix="/api/users", tags=["users"])


def _parse_uuid(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id",
        ) from exc


async def _get_user_by_id(db: AsyncSession, user_id: str) -> User:
    stmt = select(User).where(User.id == _parse_uuid(user_id))
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _ensure_admin(current_user: dict) -> None:
    if current_user.get("role") not in {UserRole.NGO_ADMIN.value, UserRole.SUPER_ADMIN.value}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def _apply_updates(user: User, payload) -> bool:
    changed = False
    for field, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(user, field) and value is not None:
            setattr(user, field, value)
            changed = True
    return changed


@router.get("/me", response_model=UserResponse)
async def read_my_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user's profile."""
    user = await _get_user_by_id(db, current_user["sub"])
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    request: UserProfileUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated user's own profile."""
    user = await _get_user_by_id(db, current_user["sub"])

    if request.email and request.email != user.email:
        stmt = select(User).where(User.email == request.email, User.id != user.id)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    _apply_updates(user, request)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    is_verified: bool | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1),
):
    """List users with pagination and filters."""
    _ensure_admin(current_user)

    filters = []
    if role is not None:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_verified is not None:
        filters.append(User.is_verified == is_verified)
    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                User.full_name.ilike(search_term),
                User.phone_number.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    count_stmt = select(func.count()).select_from(User)
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    if filters:
        stmt = stmt.where(*filters)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single user by id."""
    _ensure_admin(current_user)
    user = await _get_user_by_id(db, user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserAdminUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin update for a user record."""
    _ensure_admin(current_user)
    user = await _get_user_by_id(db, user_id)

    if request.email and request.email != user.email:
        stmt = select(User).where(User.email == request.email, User.id != user.id)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )

    if request.phone_number and request.phone_number != user.phone_number:
        stmt = select(User).where(User.phone_number == request.phone_number, User.id != user.id)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use",
            )

    _apply_updates(user, request)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a user by marking the account inactive."""
    _ensure_admin(current_user)
    user = await _get_user_by_id(db, user_id)

    user.is_active = False
    await db.commit()

    return MessageResponse(
        success=True,
        message="User deactivated successfully",
    )

