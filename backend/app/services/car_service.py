from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime

from app.db.mongo import get_collection
from app.models.car import CarCreate, CarUpdate, CarInDB

class CarService:
    """Service xử lý CRUD operations cho xe"""
    
    def __init__(self):
        self.collection_name = "cars"
    
    @staticmethod
    def car_helper(car: dict) -> dict:
        """Convert MongoDB document to response dict"""
        return {
            "_id": str(car["_id"]),
            "name": car.get("name"),
            "seats": car.get("seats"),
            "type": car.get("type"),
            "origin": car.get("origin"),
            "dimensions": car.get("dimensions"),
            "wheelbase": car.get("wheelbase"),
            "engine": car.get("engine"),
            "fuel": car.get("fuel"),
            "fuel_tank": car.get("fuel_tank"),
            "max_power": car.get("max_power"),
            "max_torque": car.get("max_torque"),
            "transmission": car.get("transmission"),
            "drivetrain": car.get("drivetrain"),
            "suspension": car.get("suspension"),
            "brakes": car.get("brakes"),
            "steering": car.get("steering"),
            "wheels": car.get("wheels"),
            "ground_clearance": car.get("ground_clearance"),
            "price": car.get("price"),
            "created_at": car.get("created_at"),
            "updated_at": car.get("updated_at"),
        }
    
    async def get_all_cars(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Lấy tất cả xe"""
        collection = get_collection(self.collection_name)
        cars = []
        
        async for car in collection.find().skip(skip).limit(limit).sort("created_at", -1):
            cars.append(self.car_helper(car))
        
        return cars
    
    async def get_car_by_id(self, car_id: str) -> Optional[dict]:
        """Lấy xe theo ID"""
        if not ObjectId.is_valid(car_id):
            return None
        
        collection = get_collection(self.collection_name)
        car = await collection.find_one({"_id": ObjectId(car_id)})
        
        if car:
            return self.car_helper(car)
        return None
    
    async def get_car_by_name(self, name: str) -> Optional[dict]:
        """Lấy xe theo tên (exact match)"""
        collection = get_collection(self.collection_name)
        car = await collection.find_one({"name": name})
        
        if car:
            return self.car_helper(car)
        return None
    
    async def search_cars(self, keyword: str) -> List[dict]:
        """Tìm kiếm xe theo keyword"""
        collection = get_collection(self.collection_name)
        cars = []
        
        # Tìm kiếm không phân biệt hoa thường
        async for car in collection.find({
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"type": {"$regex": keyword, "$options": "i"}},
                {"engine": {"$regex": keyword, "$options": "i"}}
            ]
        }):
            cars.append(self.car_helper(car))
        
        return cars
    
    async def create_car(self, car_data: CarCreate) -> dict:
        """Tạo xe mới"""
        collection = get_collection(self.collection_name)
        
        # Kiểm tra trùng tên
        existing = await collection.find_one({"name": car_data.name})
        if existing:
            raise ValueError(f"Car '{car_data.name}' already exists")
        
        # Chuẩn bị dữ liệu
        car_dict = car_data.model_dump()
        car_dict["created_at"] = datetime.utcnow()
        car_dict["updated_at"] = datetime.utcnow()
        
        # Insert
        result = await collection.insert_one(car_dict)
        
        # Lấy document vừa tạo
        new_car = await collection.find_one({"_id": result.inserted_id})
        return self.car_helper(new_car)
    
    async def update_car(self, car_id: str, car_data: CarUpdate) -> Optional[dict]:
        """Cập nhật xe"""
        if not ObjectId.is_valid(car_id):
            return None
        
        collection = get_collection(self.collection_name)
        
        # Kiểm tra xe có tồn tại không
        existing = await collection.find_one({"_id": ObjectId(car_id)})
        if not existing:
            return None
        
        # Chỉ update các field không None
        update_data = {k: v for k, v in car_data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update
        await collection.update_one(
            {"_id": ObjectId(car_id)},
            {"$set": update_data}
        )
        
        # Lấy document đã update
        updated_car = await collection.find_one({"_id": ObjectId(car_id)})
        return self.car_helper(updated_car)
    
    async def delete_car(self, car_id: str) -> bool:
        """Xóa xe"""
        if not ObjectId.is_valid(car_id):
            return False
        
        collection = get_collection(self.collection_name)
        result = await collection.delete_one({"_id": ObjectId(car_id)})
        
        return result.deleted_count > 0
    
    async def get_cars_by_type(self, car_type: str) -> List[dict]:
        """Lấy xe theo loại (SUV, Sedan, etc.)"""
        collection = get_collection(self.collection_name)
        cars = []
        
        async for car in collection.find({"type": car_type}):
            cars.append(self.car_helper(car))
        
        return cars
    
    async def get_stats(self) -> Dict:
        """Lấy thống kê về xe"""
        collection = get_collection(self.collection_name)
        
        total = await collection.count_documents({})
        
        # Thống kê theo type
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        type_stats = []
        async for item in collection.aggregate(pipeline):
            type_stats.append({
                "type": item["_id"],
                "count": item["count"]
            })
        
        return {
            "total_cars": total,
            "by_type": type_stats
        }

# Singleton instance
car_service = CarService()