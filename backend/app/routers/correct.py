from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime

from app.db.mongo import get_collection
from app.models.correct import CorrectionRequest

router = APIRouter(prefix="/correct", tags=["Correction"])

@router.post("/")
async def submit_correction(correction: CorrectionRequest):
    """
    Gửi correction cho kết quả nhận diện sai
    
    Args:
        correction: Thông tin correction
        
    Returns:
        Success status
    """
    try:
        # Lưu correction vào collection riêng
        collection = get_collection("corrections")
        
        correction_dict = correction.model_dump()
        correction_dict["timestamp"] = datetime.utcnow()
        correction_dict["status"] = "pending"  # pending, approved, rejected
        
        result = await collection.insert_one(correction_dict)
        
        return {
            "success": True,
            "message": "Correction submitted successfully",
            "correction_id": str(result.inserted_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_all_corrections(
    status: str = None,
    skip: int = 0,
    limit: int = 50
):
    """
    Lấy danh sách corrections
    
    Args:
        status: Filter theo status (pending, approved, rejected)
        skip: Pagination offset
        limit: Số lượng records
    """
    try:
        collection = get_collection("corrections")
        
        query = {}
        if status:
            query["status"] = status
        
        corrections = []
        async for correction in collection.find(query).sort("timestamp", -1).skip(skip).limit(limit):
            corrections.append({
                "_id": str(correction["_id"]),
                "filename": correction.get("filename"),
                "index": correction.get("index"),
                "new_class_name": correction.get("new_class_name"),
                "status": correction.get("status"),
                "timestamp": correction.get("timestamp")
            })
        
        return corrections
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{correction_id}/approve")
async def approve_correction(correction_id: str):
    """Phê duyệt correction"""
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="Invalid correction ID")
    
    try:
        collection = get_collection("corrections")
        
        result = await collection.update_one(
            {"_id": ObjectId(correction_id)},
            {"$set": {
                "status": "approved",
                "approved_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Correction not found")
        
        return {"success": True, "message": "Correction approved"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{correction_id}/reject")
async def reject_correction(correction_id: str):
    """Từ chối correction"""
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="Invalid correction ID")
    
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
            raise HTTPException(status_code=404, detail="Correction not found")
        
        return {"success": True, "message": "Correction rejected"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{correction_id}")
async def delete_correction(correction_id: str):
    """Xóa correction"""
    if not ObjectId.is_valid(correction_id):
        raise HTTPException(status_code=400, detail="Invalid correction ID")
    
    try:
        collection = get_collection("corrections")
        result = await collection.delete_one({"_id": ObjectId(correction_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Correction not found")
        
        return {"success": True, "message": "Correction deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_correction_stats():
    """Thống kê corrections"""
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