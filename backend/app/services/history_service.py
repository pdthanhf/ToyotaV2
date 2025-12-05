from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime, timedelta

from app.db.mongo import get_collection
from app.models.history import HistoryCreate
from app.utils.cloudinary_utils import cloudinary_service

class HistoryService:
    """Service xử lý lịch sử nhận diện"""
    
    def __init__(self):
        self.collection_name = "history"
    
    @staticmethod
    def history_helper(history: dict) -> dict:
        """Convert MongoDB document to response dict"""
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
    
    async def create_history(self, history_data: HistoryCreate) -> dict:
        """Tạo record lịch sử mới"""
        collection = get_collection(self.collection_name)
        
        history_dict = history_data.model_dump()
        history_dict["timestamp"] = datetime.utcnow()
        
        result = await collection.insert_one(history_dict)
        
        new_history = await collection.find_one({"_id": result.inserted_id})
        return self.history_helper(new_history)
    
    async def get_all_history(
        self, 
        skip: int = 0, 
        limit: int = 50,
        days: Optional[int] = None
    ) -> List[dict]:
        """Lấy lịch sử với pagination và filter"""
        collection = get_collection(self.collection_name)
        
        # Build query
        query = {}
        if days:
            date_from = datetime.utcnow() - timedelta(days=days)
            query["timestamp"] = {"$gte": date_from}
        
        history_list = []
        async for history in collection.find(query).sort("timestamp", -1).skip(skip).limit(limit):
            history_list.append(self.history_helper(history))
        
        return history_list
    
    async def get_history_by_id(self, history_id: str) -> Optional[dict]:
        """Lấy chi tiết một record"""
        if not ObjectId.is_valid(history_id):
            return None
        
        collection = get_collection(self.collection_name)
        history = await collection.find_one({"_id": ObjectId(history_id)})
        
        if history:
            return self.history_helper(history)
        return None
    
    async def delete_history(self, history_id: str) -> bool:
        """Xóa record và ảnh trên Cloudinary"""
        if not ObjectId.is_valid(history_id):
            return False
        
        collection = get_collection(self.collection_name)
        history = await collection.find_one({"_id": ObjectId(history_id)})
        
        if not history:
            return False
        
        # Xóa ảnh trên Cloudinary
        public_id = history.get("cloudinary_public_id")
        if public_id:
            # Xóa ảnh gốc
            cloudinary_service.delete_image(public_id)
            
            # Xóa ảnh result (nếu có)
            result_public_id = public_id.replace("/originals/", "/results/") + "_result"
            cloudinary_service.delete_image(result_public_id)
        
        # Xóa record trong MongoDB
        result = await collection.delete_one({"_id": ObjectId(history_id)})
        return result.deleted_count > 0
    
    async def get_stats(self) -> Dict:
        """Lấy thống kê lịch sử"""
        collection = get_collection(self.collection_name)
        
        # Tổng số
        total = await collection.count_documents({})
        
        # Hôm nay
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = await collection.count_documents({"timestamp": {"$gte": today_start}})
        
        # 7 ngày
        week_start = datetime.utcnow() - timedelta(days=7)
        week_count = await collection.count_documents({"timestamp": {"$gte": week_start}})
        
        # 30 ngày
        month_start = datetime.utcnow() - timedelta(days=30)
        month_count = await collection.count_documents({"timestamp": {"$gte": month_start}})
        
        # Thống kê theo xe được nhận diện
        pipeline = [
            {"$unwind": "$detections"},
            {"$group": {
                "_id": "$detections.class_name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_detected = []
        async for item in collection.aggregate(pipeline):
            top_detected.append({
                "car_name": item["_id"],
                "count": item["count"]
            })
        
        return {
            "total_detections": total,
            "today": today_count,
            "last_7_days": week_count,
            "last_30_days": month_count,
            "top_detected_cars": top_detected
        }
    
    async def search_by_car_name(self, car_name: str) -> List[dict]:
        """Tìm lịch sử theo tên xe"""
        collection = get_collection(self.collection_name)
        
        history_list = []
        async for history in collection.find({
            "detections.class_name": {"$regex": car_name, "$options": "i"}
        }).sort("timestamp", -1):
            history_list.append(self.history_helper(history))
        
        return history_list

# Singleton instance
history_service = HistoryService()