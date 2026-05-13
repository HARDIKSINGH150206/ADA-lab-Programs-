"""Authentication schemas for request/response validation"""
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class PhoneFieldValidator:
    """Validator for phone numbers"""
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate and format phone number"""
        # Remove any non-digit characters except an optional leading +
        cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
        if cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")):
            raise ValueError("Invalid phone number format")
        
        if not cleaned:
            raise ValueError("Invalid phone number format")
        
        return cleaned


# ==================== Request Schemas ====================

class RegisterRequest(BaseModel):
    """User registration request"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    state: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        return PhoneFieldValidator.validate_phone(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "919876543210",
                "full_name": "John Doe",
                "email": "john@example.com",
                "state": "Maharashtra",
                "password": "SecurePass123!",
            }
        }


class VerifyOTPRequest(BaseModel):
    """OTP verification request"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=6, max_length=6)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        return PhoneFieldValidator.validate_phone(v)
    
    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit():
            raise ValueError("OTP must contain only digits")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "919876543210",
                "otp": "123456",
            }
        }


class SendOTPRequest(BaseModel):
    """Send OTP request"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        return PhoneFieldValidator.validate_phone(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "919876543210",
            }
        }


class LoginRequest(BaseModel):
    """User login request"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        return PhoneFieldValidator.validate_phone(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "919876543210",
                "password": "SecurePass123!",
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            }
        }


# ==================== Response Schemas ====================

class OTPResponse(BaseModel):
    """OTP send response"""
    success: bool
    message: str
    expires_in_seconds: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "OTP sent successfully",
                "expires_in_seconds": 300,
            }
        }


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in_seconds": 86400,
            }
        }


class UserResponse(BaseModel):
    """User response"""
    id: str
    phone_number: str
    full_name: Optional[str]
    email: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    state: Optional[str]
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "phone_number": "919876543210",
                "full_name": "John Doe",
                "email": "john@example.com",
                "role": "worker",
                "is_active": True,
                "is_verified": True,
                "state": "Maharashtra",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Worker rights advocate",
                "created_at": "2026-05-14T10:30:00Z",
            }
        }
    )
    
    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @field_validator("role", mode="before")
    @classmethod
    def convert_role_to_str(cls, v):
        if hasattr(v, "value"):  # Enum
            return v.value
        return v


class LoginResponse(BaseModel):
    """Login response"""
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "phone_number": "919876543210",
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "role": "worker",
                    "is_active": True,
                    "is_verified": True,
                    "state": "Maharashtra",
                    "created_at": "2026-05-14T10:30:00Z",
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation successful",
            }
        }
