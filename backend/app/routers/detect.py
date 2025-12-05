from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from io import BytesIO
from PIL import Image
from datetime import datetime
import uuid

from app.services.detection_service import DetectionService
from app.utils.cloudinary_utils import cloudinary_service
from app.db.mongo import get_collection
from app.models.history import HistoryCreate, Detection
from app.core.config import settings

# DANH SÁCH CLASS NAMES (Phải khớp thứ tự 100% với file data.yaml dùng để train)
class_names = [
    # --- 22 XE CŨ ---
    'GT86',
    'Toyota 4Runner_SUV',
    'Toyota 86_sport',
    'Toyota Alphard_mpv',
    'Toyota Aygo_hatchback',
    'Toyota Camry XSE',
    'Toyota Camry XV40',
    'Toyota Camry XV50',
    'Toyota Camry_Hybrid',
    'Toyota Camry_sedan',
    'Toyota Corolla Altis_sedan',
    'Toyota Corolla EX_sedan',
    'Toyota Corolla Furia',
    'Toyota Crown_sedan',
    'Toyota GT86',
    'Toyota Land Cruiser_suv',
    'Toyota Prado_suv',
    'Toyota Prius_hybrid',
    'Toyota RAV4_suv',
    'Toyota Tundra_pickup',
    'Toyota Vios_sedan',
    'Toyota Yaris_hatchback',
    
    # --- 19 XE MỚI THÊM ---
    'Toyota Vios',
    'Toyota Camry',
    'Toyota Fortuner',
    'Toyota Yaris Cross',
    'Toyota Supra',
    'Alphard',
    'Toyota Innova',
    'Toyota Yaris',
    'Toyota Corolla Altis',
    'Toyota Avanza',
    'Toyota Prius',
    'Toyota Rush',
    'Toyota Wigo',
    'Toyota Hilux',
    'Toyota Land Cruiser',
    'Toyota RAV4',
    'Toyota Innova Cross',
    'Toyota Veloz Cross',
    'Toyota Raize'
]


router = APIRouter(prefix="/detect", tags=["Detection"])
detection_service = DetectionService()

@router.post("/detect")
async def detect_cars(image: UploadFile = File(...)):
    """
    Nhận diện xe từ ảnh upload và lưu vào Cloudinary + MongoDB
    
    Flow:
    1. Validate và đọc ảnh
    2. Upload ảnh gốc lên Cloudinary
    3. Nhận diện bằng YOLOv8
    4. Upload ảnh kết quả (có bounding box) lên Cloudinary
    5. Lưu thông tin vào MongoDB History
    6. Trả về kết quả cho Frontend
    """
    
    # ====== STEP 1: Validate ======
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await image.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        # ====== STEP 2: Upload ảnh gốc lên Cloudinary ======
        unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        original_filename = image.filename.rsplit('.', 1)[0]  # Loại bỏ extension
        
        # Upload ảnh gốc
        original_upload = cloudinary_service.upload_image(
            BytesIO(contents),
            folder=f"{settings.CLOUDINARY_FOLDER}/originals",
            public_id=f"{original_filename}_{unique_id}",
            tags=["original", "toyota", "detection"]
        )
        
        if not original_upload.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to upload original image: {original_upload.get('error')}"
            )
        
        original_url = original_upload.get("url")
        original_public_id = original_upload.get("public_id")
        
        # ====== STEP 3: Nhận diện bằng YOLOv8 ======
        img = Image.open(BytesIO(contents))
        detection_results = detection_service.detect(img)
        
        # ====== STEP 4: Upload ảnh kết quả lên Cloudinary ======
        result_url = None
        result_public_id = None
        
        if detection_results.get("annotated_image"):
            result_upload = cloudinary_service.upload_pil_image(
                detection_results["annotated_image"],
                folder=f"{settings.CLOUDINARY_FOLDER}/results",
                public_id=f"{original_filename}_{unique_id}_result",
                tags=["result", "toyota", "detection", "annotated"]
            )
            
            if result_upload.get("success"):
                result_url = result_upload.get("url")
                result_public_id = result_upload.get("public_id")
        
        # ====== STEP 5: Lưu vào MongoDB History ======
        detections = [
            Detection(
                class_name=det.get("class_name"),
                confidence=det.get("confidence"),
                bbox=det.get("bbox", {}),
                is_corrected=False
            )
            for det in detection_results.get("detections", [])
        ]
        
        history_data = HistoryCreate(
            filename=image.filename,
            original_image_url=original_url,
            result_image_url=result_url,
            detections=detections,
            cloudinary_public_id=original_public_id  # Để xóa sau này nếu cần
        )
        
        collection = get_collection("history")
        history_dict = history_data.model_dump()
        history_dict["timestamp"] = datetime.utcnow()
        
        result = await collection.insert_one(history_dict)
        
        # ====== STEP 6: Trả về kết quả ======
        return {
            "success": True,
            "filename": image.filename,
            "detections": [det.model_dump() for det in detections],
            "original_image_url": original_url,
            "result_image_url": result_url,
            "thumbnail_url": cloudinary_service.get_thumbnail_url(original_public_id, 300),
            "history_id": str(result.inserted_id)
        }
        
    except Exception as e:
        # Nếu có lỗi, xóa ảnh đã upload trên Cloudinary
        if original_public_id:
            cloudinary_service.delete_image(original_public_id)
        if result_public_id:
            cloudinary_service.delete_image(result_public_id)
        
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.get("/classes")
async def get_available_classes():
    """Lấy danh sách các class xe có thể nhận diện"""
    try:
        return detection_service.get_classes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-only")
async def upload_image_only(image: UploadFile = File(...)):
    """
    Chỉ upload ảnh lên Cloudinary (không nhận diện)
    Dùng cho testing hoặc upload manual
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await image.read()
    
    try:
        result = cloudinary_service.upload_image(
            BytesIO(contents),
            folder=settings.CLOUDINARY_FOLDER,
            tags=["manual_upload", "toyota"]
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "url": result.get("url"),
            "public_id": result.get("public_id"),
            "thumbnail": cloudinary_service.get_thumbnail_url(result.get("public_id"))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))