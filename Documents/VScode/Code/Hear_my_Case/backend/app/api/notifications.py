"""Notification management routes"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import get_current_user
from app.db.database import get_db
from app.models.notification import Notification
from app.models.user import UserRole
from app.schemas.auth import MessageResponse
from app.schemas.notifications import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
    NotificationUpdateRequest,
)
from app.services.notifications import create_notification, mark_all_notifications_read

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _parse_uuid(value: str, label: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {label}") from exc


def _is_admin(current_user: dict) -> bool:
    return current_user.get("role") in {UserRole.NGO_ADMIN.value, UserRole.SUPER_ADMIN.value}


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
):
    """List notifications for the current user."""
    user_id = _parse_uuid(current_user["sub"], "user id")

    filters = [Notification.user_id == user_id]
    if unread_only:
        filters.append(Notification.is_read.is_(False))

    count_stmt = select(func.count()).select_from(Notification).where(*filters)
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(Notification).where(*filters).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/unread-count")
async def unread_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the unread notification count."""
    user_id = _parse_uuid(current_user["sub"], "user id")
    stmt = select(func.count()).select_from(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read.is_(False),
    )
    count = (await db.execute(stmt)).scalar_one()
    return {"unread_count": count}


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_endpoint(
    request: NotificationCreateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a notification for a user."""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    notification = await create_notification(
        db,
        user_id=_parse_uuid(request.user_id, "user id"),
        title=request.title,
        message=request.message,
        notification_type=request.notification_type,
        related_case_id=_parse_uuid(request.related_case_id, "case id") if request.related_case_id else None,
        related_group_id=_parse_uuid(request.related_group_id, "group id") if request.related_group_id else None,
    )
    return NotificationResponse.model_validate(notification)


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    request: NotificationUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update notification read/sent state."""
    notification_uuid = _parse_uuid(notification_id, "notification id")
    stmt = select(Notification).where(Notification.id == notification_uuid)
    result = await db.execute(stmt)
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if str(notification.user_id) != current_user["sub"] and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    for field, value in request.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(notification, field, value)
    await db.commit()
    await db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.patch("/mark-all-read", response_model=MessageResponse)
async def mark_all_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    user_id = _parse_uuid(current_user["sub"], "user id")
    count = await mark_all_notifications_read(db, user_id)
    return MessageResponse(success=True, message=f"Marked {count} notifications as read")

