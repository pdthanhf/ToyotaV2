from pydantic import BaseModel, Field
from typing import Optional

class CorrectionRequest(BaseModel):
    """Schema cho correction request"""
    filename: str = Field(..., description="Tên file ảnh")
    index: int = Field(..., description="Index của detection bị sai", ge=0)
    old_class_name: str = Field(..., description="Tên class cũ (sai)")
    new_class_name: str = Field(..., description="Tên class đúng")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "car_image.jpg",
                "index": 0,
                "old_class_name": "Toyota Vios",
                "new_class_name": "Toyota Camry"
            }
        }