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

# Router này đang có prefix là /detect
# Khi main.py gọi, đường dẫn sẽ là /api/detect/...
router = APIRouter(prefix="/detect", tags=["Detection"])
detection_service = DetectionService()

@router.post("/detect")  # -> URL thực tế: /api/detect/detect
async def detect_cars(image: UploadFile = File(...)):
    # Khai báo biến trước try để tránh lỗi UnboundLocalError khi vào except
    original_public_id = None
    result_public_id = None

    # ====== STEP 1: Validate ======
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await image.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        # ====== STEP 2: Upload ảnh gốc lên Cloudinary ======
        unique_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        original_filename = image.filename.rsplit('.', 1)[0]
        
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
        original_public_id = original_upload.get("public_id") # Đã gán giá trị
        
        # ====== STEP 3: Nhận diện bằng YOLOv8 ======
        img = Image.open(BytesIO(contents))
        detection_results = detection_service.detect(img)
        
        # ====== STEP 4: Upload ảnh kết quả lên Cloudinary ======
        result_url = None
        
        if detection_results.get("annotated_image"):
            result_upload = cloudinary_service.upload_pil_image(
                detection_results["annotated_image"],
                folder=f"{settings.CLOUDINARY_FOLDER}/results",
                public_id=f"{original_filename}_{unique_id}_result",
                tags=["result", "toyota", "detection", "annotated"]
            )
            
            if result_upload.get("success"):
                result_url = result_upload.get("url")
                result_public_id = result_upload.get("public_id") # Đã gán giá trị
        
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
            cloudinary_public_id=original_public_id
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
        print(f" Error processing image: {str(e)}") # Log lỗi ra terminal để dễ debug
        # Chỉ xóa nếu biến đã có giá trị (không phải None)
        if original_public_id:
            cloudinary_service.delete_image(original_public_id)
        if result_public_id:
            cloudinary_service.delete_image(result_public_id)
        
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")

# ... (Các hàm get/classes và upload-only giữ nguyên) ...
@router.get("/classes")
async def get_available_classes():
    try:
        return detection_service.get_classes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-only")
async def upload_image_only(image: UploadFile = File(...)):
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