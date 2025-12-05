
try:
    from pydantic_settings import BaseSettings  # Pydantic V2
except ImportError:
    from pydantic import BaseSettings  # Pydantic V1 fallback

from typing import List

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "toyota_v2_db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    # Upload
    MAX_FILE_SIZE: int = 10485760
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Model
    MODEL_PATH: str = "app/car_classifier/best.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = "db2y3g4sg"
    CLOUDINARY_API_KEY: str = "628965261272739"
    CLOUDINARY_API_SECRET: str = "FOpWcAOCC76c1vHQ8HUeZ6A_Chc"
    CLOUDINARY_FOLDER: str = "toyota_v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Thêm dòng này để không bắt buộc các field
        extra = "allow"

settings = Settings()