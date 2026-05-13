"""Evidence schemas for file upload and metadata"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, Field


class EvidenceResponse(BaseModel):
    """Evidence response schema"""

    id: str
    case_id: str
    file_name: str
    file_url: str
    file_size: Optional[str] = None
    mime_type: Optional[str] = None
    category: Optional[str] = None
    confidence_score: Optional[str] = None
    auto_tags: Optional[list[str]] = None
    extracted_text: Optional[str] = None
    ai_summary: Optional[str] = None
    user_description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceListResponse(BaseModel):
    """Paginated evidence response"""

    items: list[EvidenceResponse]
    total: int
    skip: int
    limit: int


class EvidenceMetadataResponse(BaseModel):
    """Response returned after upload"""

    evidence: EvidenceResponse
    extracted_text: Optional[str] = None
    auto_tags: list[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None


class EvidenceUpdateRequest(BaseModel):
    """Update evidence metadata request"""

    user_description: Optional[str] = None
    category: Optional[str] = None
