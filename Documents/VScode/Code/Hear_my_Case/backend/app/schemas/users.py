"""User management schemas"""
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

from app.models.user import UserRole
from app.schemas.auth import UserResponse


class UserProfileUpdateRequest(BaseModel):
    """Self-service profile update request"""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "state": "Maharashtra",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Worker rights advocate",
            }
        }
    )


class UserAdminUpdateRequest(BaseModel):
    """Admin update request for user management"""

    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=15)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone_number": "919876543210",
                "role": "worker",
                "is_active": True,
                "is_verified": True,
                "state": "Maharashtra",
            }
        }
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        cleaned = "".join(c for c in v if c.isdigit() or c == "+")
        if cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")):
            raise ValueError("Invalid phone number format")
        if not cleaned:
            raise ValueError("Invalid phone number format")
        return cleaned


class UserListResponse(BaseModel):
    """Paginated user list response"""

    items: list[UserResponse]
    total: int
    skip: int
    limit: int
