from pydantic import BaseModel, Field
from typing import Optional

class CorrectionRequest(BaseModel):
    """Schema cho correction request (Active Learning Feedback)"""
    
    image_url: str = Field(..., description="URL ảnh trên Cloudinary để truy xuất lại khi train")
    predicted_label: str = Field(..., description="Tên dòng xe Model dự đoán (ví dụ: toyota_vios)")
    actual_label: str = Field(..., description="Tên dòng xe đúng thực tế (ví dụ: toyota_camry)")
    confidence: float = Field(..., description="Độ tin cậy của dự đoán (0.0 - 1.0)")
    is_correct: bool = Field(..., description="True nếu người dùng xác nhận đúng, False nếu sai")
    timestamp: Optional[str] = Field(None, description="Thời gian gửi feedback (ISO String)")

    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "http://res.cloudinary.com/demo/image/upload/v123/car.jpg",
                "predicted_label": "toyota_vios",
                "actual_label": "toyota_camry",
                "confidence": 0.85,
                "is_correct": False,
                "timestamp": "2024-12-07T12:00:00.000Z"
            }
        }