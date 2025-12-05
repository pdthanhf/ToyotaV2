from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from app.db.mongo import get_collection
from app.utils.cloudinary_utils import cloudinary_service

router = APIRouter(prefix="/history", tags=["History"])

def history_helper(history) -> dict:
    """Convert MongoDB document to dict"""
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
        "timestamp": history.get("timestamp"),
    }

@router.get("/", response_model=List[dict])
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    days: Optional[int] = Query(None, ge=1, le=365)
):
    """
    Lấy lịch sử nhận diện
    
    Args:
        limit: Số record tối đa (mặc định 50)
        skip: Bỏ qua bao nhiêu record (pagination)
        days: Lọc theo số ngày gần đây (optional)
    """
    collection = get_collection("history")
    
    # Filter by date if specified
    query = {}
    if days:
        date_from = datetime.utcnow() - timedelta(days=days)
        query["timestamp"] = {"$gte": date_from}
    
    history_list = []
    async for history in collection.find(query).sort("timestamp", -1).skip(skip).limit(limit):
        history_list.append(history_helper(history))
    
    return history_list


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


@router.get("/stats/summary")
async def get_history_stats():
    """Lấy thống kê tổng quan"""
    collection = get_collection("history")
    
    total = await collection.count_documents({})
    
    # Số lượng nhận diện theo ngày
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await collection.count_documents({"timestamp": {"$gte": today_start}})
    
    # Số lượng 7 ngày gần đây
    week_start = datetime.utcnow() - timedelta(days=7)
    week_count = await collection.count_documents({"timestamp": {"$gte": week_start}})
    
    return {
        "total_detections": total,
        "today": today_count,
        "last_7_days": week_count
    }