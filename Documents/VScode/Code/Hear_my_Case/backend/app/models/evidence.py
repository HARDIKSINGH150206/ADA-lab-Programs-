"""Evidence model for database"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.db.database import Base


class Evidence(Base):
    """Evidence model for file uploads"""
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)  # S3 URL
    file_size = Column(String(50), nullable=True)  # in bytes
    mime_type = Column(String(100), nullable=True)
    
    # Auto-tagged by AI
    category = Column(String(50), nullable=True)  # wage_slip, contract, message, photo, voice_note, etc.
    confidence_score = Column(String(10), nullable=True)  # 0.0 to 1.0
    auto_tags = Column(JSON, nullable=True)
    extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    
    # User annotation
    user_description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Evidence {self.file_name} - {self.category}>"
