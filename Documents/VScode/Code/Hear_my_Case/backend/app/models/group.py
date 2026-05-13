"""Group model for collective legal action"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.database import Base


class Group(Base):
    """Group model for collective legal cases"""
    __tablename__ = "groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(String(100), nullable=False, index=True)
    case_type = Column(String(50), nullable=False, index=True)
    notice_status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, sent, completed
    
    # Lawyer assignment
    assigned_lawyer_id = Column(UUID(as_uuid=True), ForeignKey("lawyers.id"), nullable=True)
    
    # Group details
    member_count = Column(Integer, default=0)
    notice_url = Column(String(500), nullable=True)  # S3 URL to collective notice
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Group {self.state} - {self.case_type} ({self.notice_status})>"
