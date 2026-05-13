"""Notification schemas"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Notification response schema"""

    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    is_sent: bool
    related_case_id: Optional[str] = None
    related_group_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated notifications"""

    items: list[NotificationResponse]
    total: int
    skip: int
    limit: int


class NotificationCreateRequest(BaseModel):
    """Create notification request"""

    user_id: str
    title: str
    message: str
    notification_type: str = "info"
    related_case_id: Optional[str] = None
    related_group_id: Optional[str] = None


class NotificationUpdateRequest(BaseModel):
    """Update notification request"""

    is_read: Optional[bool] = None
    is_sent: Optional[bool] = None

