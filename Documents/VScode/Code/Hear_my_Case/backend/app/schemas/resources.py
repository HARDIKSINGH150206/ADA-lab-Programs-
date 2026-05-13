"""Shared CRUD schemas for groups, lawyers, and NGOs"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GroupBase(BaseModel):
    state: str = Field(..., min_length=2, max_length=100)
    case_type: str = Field(..., min_length=2, max_length=50)
    notice_status: str = Field(default="pending", max_length=50)
    assigned_lawyer_id: Optional[str] = None
    member_count: int = 0
    notice_url: Optional[str] = Field(default=None, max_length=500)


class GroupCreateRequest(GroupBase):
    pass


class GroupUpdateRequest(BaseModel):
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    case_type: Optional[str] = Field(default=None, min_length=2, max_length=50)
    notice_status: Optional[str] = Field(default=None, max_length=50)
    assigned_lawyer_id: Optional[str] = None
    member_count: Optional[int] = None
    notice_url: Optional[str] = Field(default=None, max_length=500)


class GroupResponse(GroupBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LawyerBase(BaseModel):
    user_id: str
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = Field(default=None, max_length=500)
    years_of_experience: Optional[int] = None
    specializations: Optional[list[str]] = None
    bar_council_id: Optional[str] = Field(default=None, max_length=100)
    is_available: bool = True
    available_for_group_cases: bool = False
    states_served: Optional[list[str]] = None
    average_rating: Optional[str] = "0.0"
    total_cases: int = 0
    active_cases: int = 0
    office_address: Optional[str] = Field(default=None, max_length=500)
    languages: Optional[list[str]] = None


class LawyerCreateRequest(LawyerBase):
    pass


class LawyerUpdateRequest(BaseModel):
    user_id: Optional[str] = None
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=20)
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = Field(default=None, max_length=500)
    years_of_experience: Optional[int] = None
    specializations: Optional[list[str]] = None
    bar_council_id: Optional[str] = Field(default=None, max_length=100)
    is_available: Optional[bool] = None
    available_for_group_cases: Optional[bool] = None
    states_served: Optional[list[str]] = None
    average_rating: Optional[str] = None
    total_cases: Optional[int] = None
    active_cases: Optional[int] = None
    office_address: Optional[str] = Field(default=None, max_length=500)
    languages: Optional[list[str]] = None


class LawyerResponse(LawyerBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NGOBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = None
    logo_url: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=255)
    states_served: Optional[list[str]] = None
    case_types_handled: Optional[list[str]] = None
    is_active: bool = True
    contact_person_name: Optional[str] = Field(default=None, max_length=255)
    contact_person_phone: Optional[str] = Field(default=None, max_length=20)
    average_rating: Optional[str] = "0.0"
    total_cases_handled: int = 0


class NGOCreateRequest(NGOBase):
    pass


class NGOUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    email: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = None
    logo_url: Optional[str] = Field(default=None, max_length=500)
    website: Optional[str] = Field(default=None, max_length=255)
    states_served: Optional[list[str]] = None
    case_types_handled: Optional[list[str]] = None
    is_active: Optional[bool] = None
    contact_person_name: Optional[str] = Field(default=None, max_length=255)
    contact_person_phone: Optional[str] = Field(default=None, max_length=20)
    average_rating: Optional[str] = None
    total_cases_handled: Optional[int] = None


class NGOResponse(NGOBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

