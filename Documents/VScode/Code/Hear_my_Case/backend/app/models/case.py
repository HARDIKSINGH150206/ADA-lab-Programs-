"""Case model for database"""
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime
from app.db.database import Base
from app.utils.constants import CASE_TYPES, CASE_STATUSES
import enum


class CaseType(str, enum.Enum):
    """Case type enumeration"""
    UNPAID_WAGES = "unpaid_wages"
    WORKPLACE_INJURY = "workplace_injury"
    HARASSMENT = "harassment"
    WRONGFUL_TERMINATION = "wrongful_termination"
    DISCRIMINATION = "discrimination"
    OTHER = "other"


class CaseStatus(str, enum.Enum):
    """Case status enumeration"""
    DRAFT = "draft"
    INTAKE_COMPLETE = "intake_complete"
    REPORT_GENERATED = "report_generated"
    LAWYER_ASSIGNED = "lawyer_assigned"
    GROUP_ASSIGNED = "group_assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class Case(Base):
    """Case model"""
    __tablename__ = "cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    case_type = Column(Enum(CaseType), nullable=False)
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT, nullable=False)
    
    # Case details
    employer_name = Column(String(255), nullable=False)
    amount_owed = Column(Float, nullable=True)
    period_start = Column(String(10), nullable=True)  # YYYY-MM-DD
    period_end = Column(String(10), nullable=True)    # YYYY-MM-DD
    contract_type = Column(String(50), nullable=True)  # written, verbal, none
    
    # AI-generated content
    case_summary = Column(JSONB, nullable=True)  # Stores AI-generated summary
    applicable_laws = Column(Text, nullable=True)
    what_should_happen = Column(Text, nullable=True)
    next_steps = Column(JSONB, nullable=True)
    
    # Group & Lawyer assignment
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Case {self.id} - {self.case_type} ({self.status})>"


class CaseStep(Base):
    """Case step/milestone model"""
    __tablename__ = "case_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    step_number = Column(String(50), nullable=False)  # e.g., "1", "2", "3"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CaseStep {self.case_id} - Step {self.step_number}>"
