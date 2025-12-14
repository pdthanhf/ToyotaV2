from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from bson import ObjectId
from datetime import datetime, timedelta # <--- 1. BỔ SUNG TIMEDELTA

from app.db.mongo import get_collection
from app.models.correct import CorrectionRequest
from app.utils.cloudinary_utils import CloudinaryService  

# Tạo router
router = APIRouter(prefix="/correct", tags=["Correction & Active Learning"])

# --- HELPER: Lấy public_id từ Cloudinary URL ---
def extract_public_id(image_url: str) -> str:
    """
    Trích xuất public_id từ URL ảnh Cloudinary.
    """
    try:
        parts = image_url.split("/upload/")
        if len(parts) > 1:
            path = parts[1]
            path_parts = path.split("/")
            # Bỏ version (v1234/) nếu có
            if path_parts[0].startswith("v"):
                path_parts.pop(0)
            filename = "/".join(path_parts)
            return filename.rsplit(".", 1)[0] # Bỏ đuôi .jpg
    except Exception:
        pass
    return ""

# --- ENDPOINTS ---

@router.post("/")
async def submit_correction(correction: CorrectionRequest):
    """
    API nhận feedback từ Frontend (Người dùng bấm Đúng/Sai)
    """
    try:
        collection = get_collection("corrections")
        
        # Chuyển đổi Pydantic model sang dict
        correction_dict = correction.model_dump()
        
        # Bổ sung các trường quản lý hệ thống
        correction_dict["created_at"] = datetime.utcnow()
        correction_dict["status"] = "pending"  # Trạng thái chờ Admin duyệt
        correction_dict["public_id"] = extract_public_id(correction.image_url)
        
        # Lưu vào MongoDB
        result = await collection.insert_one(correction_dict)
        
        return {
            "success": True,
            "message": "Đã ghi nhận phản hồi.",
            "id": str(result.inserted_id)
        }
        
    except Exception as e:
        print(f"Lỗi submit correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_corrections(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """
    Lấy danh sách feedback (Dùng cho Admin Dashboard)
    """
    try:
        collection = get_collection("corrections")
        
        query = {}
        if status:
            query["status"] = status
        
        corrections = []
        # Sort theo thời gian mới nhất
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        async for doc in cursor:
            # --- SỬA LOGIC NGÀY GIỜ TẠI ĐÂY ---
            ts = doc.get("created_at")
            if ts and isinstance(ts, datetime):
                # Cộng 7 tiếng cho giờ hiển thị
                ts = ts + timedelta(hours=7)
            # ----------------------------------

            corrections.append({
                "id": str(doc["_id"]),
                "image_url": doc.get("image_url"),
                "predicted_label": doc.get("predicted_label"),
                "actual_label": doc.get("actual_label"),
                "confidence": doc.get("confidence"),
                "is_correct": doc.get("is_correct"),
                "status": doc.get("status"),
                "created_at": ts # Dùng biến ts đã cộng giờ
            })
        
        return corrections
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{correction_id}/approve")
async def approve_correction(correction_id: str, background_tasks: BackgroundTasks):
    """
    Admin duyệt
    """
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
    
    try:
        collection = get_collection("corrections")
        
        # 1. Lấy thông tin bản ghi trước (để lấy public_id và label)
        record = await collection.find_one({"_id": ObjectId(correction_id)})
        if not record:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")

        # 2. Update trạng thái trong DB
        result = await collection.update_one(
            {"_id": ObjectId(correction_id)},
            {"$set": {
                "status": "approved",
                "approved_at": datetime.utcnow()
            }}
        )
        
        # 3. GỌI CLOUDINARY ĐỂ GẮN TAG (Chạy ngầm - Background Task)
        public_id = record.get("public_id")
        actual_label = record.get("actual_label")
        
        # Nếu có đủ thông tin, thêm task gắn tag
        if public_id and actual_label:
            background_tasks.add_task(CloudinaryService.add_tag_to_image, public_id, actual_label)

        return {"success": True, "message": "Đã duyệt và đang cập nhật nhãn trên Cloudinary."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{correction_id}/reject")
async def reject_correction(correction_id: str):
    """
    Admin từ chối
    """
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
    
    try:
        collection = get_collection("corrections")
        result = await collection.update_one(
            {"_id": ObjectId(correction_id)},
            {"$set": {
                "status": "rejected",
                "rejected_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
            
        return {"success": True, "message": "Đã từ chối."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{correction_id}")
async def delete_correction(correction_id: str):
    """
    Xóa hoàn toàn bản ghi (Dọn dẹp)
    """
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")
    
    try:
        collection = get_collection("corrections")
        result = await collection.delete_one({"_id": ObjectId(correction_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
            
        return {"success": True, "message": "Đã xóa bản ghi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_correction_stats():
    """
    Thống kê cho Dashboard
    """
    try:
        collection = get_collection("corrections")
        
        total = await collection.count_documents({})
        pending = await collection.count_documents({"status": "pending"})
        approved = await collection.count_documents({"status": "approved"})
        rejected = await collection.count_documents({"status": "rejected"})
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))