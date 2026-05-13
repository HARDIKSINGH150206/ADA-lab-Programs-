"""NGO model for database"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
from app.db.database import Base


class NGO(Base):
    """NGO model for Non-Governmental Organizations"""
    __tablename__ = "ngos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), unique=True, nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    # Details
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Service Areas
    states_served = Column(ARRAY(String), nullable=True)  # e.g., ['MH', 'GJ', 'KA']
    case_types_handled = Column(ARRAY(String), nullable=True)  # e.g., ['wage_disputes', 'harassment']
    
    # Availability
    is_active = Column(Boolean, default=True)
    contact_person_name = Column(String(255), nullable=True)
    contact_person_phone = Column(String(20), nullable=True)
    
    # Rating & Stats
    average_rating = Column(String(10), default="0.0", nullable=True)
    total_cases_handled = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<NGO {self.name}>"
