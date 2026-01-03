from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

Base = declarative_base()

class SparePart(Base):
    __tablename__ = "spare_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    material_number = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    specifications = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SparePartCreate(BaseModel):
    material_number: str
    description: str
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[str] = None
    image_path: Optional[str] = None

class SparePartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    material_number: str
    description: str
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    specifications: Optional[str] = None
    image_path: Optional[str] = None
    created_at: datetime

class SearchResult(BaseModel):
    spare_part: SparePartResponse
    confidence_score: float
    match_reason: str

class ImageUploadResponse(BaseModel):
    message: str
    search_results: List[SearchResult] 