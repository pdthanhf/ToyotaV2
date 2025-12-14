from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from app.db.mongo import get_collection
from app.utils.cloudinary_utils import cloudinary_service

router = APIRouter(prefix="/history", tags=["History"])

# --- HÀM HELPER XỬ LÝ DỮ LIỆU ---
def history_helper(history) -> dict:
    """Convert MongoDB document to dict"""
    
    # 1. Lấy thời gian gốc (UTC) từ Database
    ts = history.get("timestamp")
    
    # 2. LOGIC QUAN TRỌNG: Chuyển sang giờ Việt Nam (GMT+7) để hiển thị
    # Nếu có dữ liệu thời gian, ta cộng thêm 7 tiếng
    if ts and isinstance(ts, datetime):
        ts = ts + timedelta(hours=7)
    
    return {
        "_id": str(history["_id"]),
        "filename": history.get("filename"),
        "original_image_url": history.get("original_image_url"),
        "result_image_url": history.get("result_image_url"),
        "thumbnail_url": cloudinary_service.get_thumbnail_url(
            history.get("cloudinary_public_id"), 200
        ) if history.get("cloudinary_public_id") else None,
        "detections": history.get("detections", []),
        "cloudinary_public_id": history.get("cloudinary_public_id"),
        
        # Trả về thời gian đã được chuyển sang giờ VN
        "timestamp": ts, 
    }

# --- API LẤY DANH SÁCH LỊCH SỬ ---
@router.get("/", response_model=List[dict])
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    days: Optional[int] = Query(None, ge=1, le=365)
):
    """
    Lấy lịch sử nhận diện
    """
    collection = get_collection("history")
    
    # Filter by date if specified
    query = {}
    if days:
        # Tính mốc thời gian (UTC) cách đây 'days' ngày
        date_from = datetime.utcnow() - timedelta(days=days)
        query["timestamp"] = {"$gte": date_from}
    
    history_list = []
    # Sort timestamp -1 để lấy cái mới nhất trước
    async for history in collection.find(query).sort("timestamp", -1).skip(skip).limit(limit):
        history_list.append(history_helper(history))
    
    return history_list

# --- API LẤY CHI TIẾT 1 LỊCH SỬ ---
@router.get("/{history_id}", response_model=dict)
async def get_history_by_id(history_id: str):
    """Lấy chi tiết một record lịch sử"""
    if not ObjectId.is_valid(history_id):
        raise HTTPException(status_code=400, detail="Invalid history ID")
    
    collection = get_collection("history")
    history = await collection.find_one({"_id": ObjectId(history_id)})
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    return history_helper(history)

# --- API XÓA LỊCH SỬ ---
@router.delete("/{history_id}")
async def delete_history(history_id: str):
    """
    Xóa record lịch sử và ảnh trên Cloudinary
    """
    if not ObjectId.is_valid(history_id):
        raise HTTPException(status_code=400, detail="Invalid history ID")
    
    collection = get_collection("history")
    history = await collection.find_one({"_id": ObjectId(history_id)})
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    # Xóa ảnh trên Cloudinary
    public_id = history.get("cloudinary_public_id")
    if public_id:
        cloudinary_service.delete_image(public_id)
        # Xóa cả ảnh result (nếu có)
        result_public_id = public_id.replace("/originals/", "/results/") + "_result"
        cloudinary_service.delete_image(result_public_id)
    
    # Xóa record trong MongoDB
    await collection.delete_one({"_id": ObjectId(history_id)})
    
    return {"success": True, "message": "History deleted successfully"}

# --- API THỐNG KÊ (ĐÃ SỬA LOGIC GIỜ VN) ---
@router.get("/stats/summary")
async def get_history_stats():
    """Lấy thống kê tổng quan"""
    collection = get_collection("history")
    
    total = await collection.count_documents({})
    
    # --- LOGIC TÍNH TOÁN NGÀY HÔM NAY THEO GIỜ VIỆT NAM ---
    
    # 1. Lấy giờ hiện tại (UTC)
    now_utc = datetime.utcnow()
    
    # 2. Chuyển sang giờ VN (+7)
    now_vn = now_utc + timedelta(hours=7)
    
    # 3. Tìm thời điểm 00:00:00 của ngày hôm nay tại VN
    today_start_vn = now_vn.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 4. Quy đổi ngược lại 00:00 VN sang UTC để query Database
    # (Ví dụ: 00:00 VN ngày 15/12 là 17:00 UTC ngày 14/12)
    today_query_utc = today_start_vn - timedelta(hours=7)
    
    # Đếm số lượng từ mốc thời gian đó trở đi
    today_count = await collection.count_documents({"timestamp": {"$gte": today_query_utc}})
    
    # --- LOGIC 7 NGÀY GẦN ĐÂY ---
    # Lấy mốc 7 ngày trước so với hiện tại
    week_start_utc = datetime.utcnow() - timedelta(days=7)
    week_count = await collection.count_documents({"timestamp": {"$gte": week_start_utc}})
    
    return {
        "total_detections": total,
        "today": today_count,
        "last_7_days": week_count
    }