"""Case schemas for request/response validation"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class CaseTypeEnum(str, Enum):
    """Case type options"""
    UNPAID_WAGES = "unpaid_wages"
    WORKPLACE_INJURY = "workplace_injury"
    HARASSMENT = "harassment"
    WRONGFUL_TERMINATION = "wrongful_termination"
    DISCRIMINATION = "discrimination"
    OTHER = "other"


class CaseStatusEnum(str, Enum):
    """Case status options"""
    DRAFT = "draft"
    INTAKE_COMPLETE = "intake_complete"
    REPORT_GENERATED = "report_generated"
    LAWYER_ASSIGNED = "lawyer_assigned"
    GROUP_ASSIGNED = "group_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


# ==================== Request Schemas ====================

class CreateCaseRequest(BaseModel):
    """Create new case request"""
    case_type: CaseTypeEnum
    employer_name: str = Field(..., min_length=2, max_length=255)
    amount_owed: Optional[float] = Field(None, gt=0)
    period_start: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    period_end: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    contract_type: Optional[str] = Field(None, max_length=50)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_type": "unpaid_wages",
                "employer_name": "ABC Manufacturing",
                "amount_owed": 50000.00,
                "period_start": "2025-01-01",
                "period_end": "2026-05-13",
                "contract_type": "written",
            }
        }
    )


class UpdateCaseRequest(BaseModel):
    """Update case request"""
    case_type: Optional[CaseTypeEnum] = None
    employer_name: Optional[str] = Field(None, min_length=2, max_length=255)
    amount_owed: Optional[float] = Field(None, gt=0)
    period_start: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    period_end: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    contract_type: Optional[str] = Field(None, max_length=50)
    status: Optional[CaseStatusEnum] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "intake_complete",
                "amount_owed": 75000.00,
            }
        }
    )


# ==================== Response Schemas ====================

class CaseStepResponse(BaseModel):
    """Case step response"""
    id: str
    case_id: str
    step_number: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class CaseResponse(BaseModel):
    """Case response"""
    id: str
    user_id: str
    case_type: str
    status: str
    employer_name: str
    amount_owed: Optional[float]
    period_start: Optional[str]
    period_end: Optional[str]
    contract_type: Optional[str]
    case_summary: Optional[Any]
    applicable_laws: Optional[str]
    what_should_happen: Optional[str]
    next_steps: Optional[Any]
    group_id: Optional[str]
    lawyer_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "644e2f16-756c-436c-aa8f-33de4f769b31",
                "case_type": "unpaid_wages",
                "status": "report_generated",
                "employer_name": "ABC Manufacturing",
                "amount_owed": 50000.00,
                "period_start": "2025-01-01",
                "period_end": "2026-05-13",
                "contract_type": "written",
                "case_summary": {"summary": "Worker claim for unpaid wages..."},
                "applicable_laws": "Payment of Wages Act, 1936; The Code on Social Security, 2020",
                "what_should_happen": "Worker should receive full payment with interest...",
                "next_steps": ["File complaint with Labour Department", "Submit evidence"],
                "created_at": "2026-05-14T10:30:00Z",
            }
        }
    )


class CaseListResponse(BaseModel):
    """Paginated list of cases"""
    items: List[CaseResponse]
    total: int
    skip: int
    limit: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "skip": 0,
                "limit": 20,
            }
        }
    )
