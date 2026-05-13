"""Notification helper utilities"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    *,
    user_id,
    title: str,
    message: str,
    notification_type: str = "info",
    related_case_id=None,
    related_group_id=None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_case_id=related_case_id,
        related_group_id=related_group_id,
        is_sent=True,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_notifications_read(db: AsyncSession, user_id) -> int:
    result = await db.execute(select(Notification).where(Notification.user_id == user_id, Notification.is_read.is_(False)))
    notifications = result.scalars().all()
    for notification in notifications:
        notification.is_read = True
    await db.commit()
    return len(notifications)

