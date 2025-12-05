from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: dict
    is_corrected: bool = False

class HistoryCreate(BaseModel):
    filename: str
    original_image_url: str
    result_image_url: Optional[str] = None
    detections: List[Detection]
    cloudinary_public_id: str

class HistoryInDB(HistoryCreate):
    id: str = Field(..., alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True