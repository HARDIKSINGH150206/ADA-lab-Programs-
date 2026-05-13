"""Lawyer model for database"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
from app.db.database import Base


class Lawyer(Base):
    """Lawyer model for legal professionals"""
    __tablename__ = "lawyers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Link to User table
    
    # Profile
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    
    # Experience
    years_of_experience = Column(Integer, nullable=True)
    specializations = Column(ARRAY(String), nullable=True)  # e.g., ['labor_law', 'wage_disputes']
    bar_council_id = Column(String(100), unique=True, nullable=True)
    
    # Availability & Service Areas
    is_available = Column(Boolean, default=True)
    available_for_group_cases = Column(Boolean, default=False)
    states_served = Column(ARRAY(String), nullable=True)  # e.g., ['MH', 'GJ', 'KA']
    
    # Rating
    average_rating = Column(String(10), default="0.0", nullable=True)
    total_cases = Column(Integer, default=0)
    active_cases = Column(Integer, default=0)
    
    # Contact
    office_address = Column(String(500), nullable=True)
    languages = Column(ARRAY(String), nullable=True)  # e.g., ['en', 'hi', 'mr']
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Lawyer {self.full_name} - {', '.join(self.states_served or [])}>"
