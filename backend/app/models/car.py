from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Model con: Chi tiết từng phiên bản
class CarVersion(BaseModel):
    name: str
    price: Optional[str] = None
    specs: Optional[Dict[str, Any]] = None

# Model chính: Dòng xe
class CarBase(BaseModel):
    name: str = Field(..., description="Tên dòng xe")
    description: Optional[str] = None
    yolo_labels: Optional[List[str]] = Field(default_factory=list, description="Nhãn nhận diện YOLO")
    # Quan trọng: Trường này chứa danh sách các phiên bản
    versions: Optional[List[CarVersion]] = Field(default_factory=list)

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    yolo_labels: Optional[List[str]] = None
    versions: Optional[List[CarVersion]] = None

class CarInDB(CarBase):
    id: str = Field(..., alias="_id")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True