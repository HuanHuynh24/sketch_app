from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.config import settings
# pyrefly: ignore [missing-import]
from .base import Base, SchemaMixin


class University(Base, SchemaMixin):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    country = Column(String, index=True, nullable=False)
    city = Column(String, index=True)
    website = Column(String)
    description = Column(Text)
    
    # Relationships
    programs = relationship("UniversityProgram", back_populates="university", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UniversityProgram(Base, SchemaMixin):
    __tablename__ = "university_programs"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey(f"{settings.DB_SCHEMA}.universities.id", ondelete="CASCADE"))
    
    # Core fields for structured search
    university_name = Column(String, index=True, nullable=False) # Denormalized for faster query
    country = Column(String, index=True, nullable=False) # Denormalized
    city = Column(String, index=True) # Denormalized
    major_name = Column(String, index=True, nullable=False)
    degree_level = Column(String, index=True) # e.g., Bachelor, Master, PhD
    
    tuition_fee = Column(Float)
    currency = Column(String, default="USD")
    
    ielts_requirement = Column(Float)
    gpa_requirement = Column(Float)
    deadline = Column(DateTime(timezone=True))
    
    # Flexible schema using JSON/JSONB for things that vary a lot
    scholarship_info = Column(JSON)
    career_outcomes = Column(JSON)
    
    # Ingestion / Data Freshness (TTL) Fields
    source_url = Column(String)
    raw_json = Column(JSON)
    last_crawled_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    university = relationship("University", back_populates="programs")
