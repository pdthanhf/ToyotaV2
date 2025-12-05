from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.car import CarCreate, CarUpdate
from app.db.mongo import get_collection

router = APIRouter(prefix="/cars", tags=["Cars Management"])

def car_helper(car) -> dict:
    """
    Chuyển đổi dữ liệu từ MongoDB sang JSON chuẩn.
    Bây giờ chúng ta trả về nguyên mảng 'versions' để Frontend tự xử lý.
    """
    return {
        "id": str(car["_id"]),
        "name": car.get("name"),
        "description": car.get("description"),
        "yolo_labels": car.get("yolo_labels", []),
        # Quan trọng: Trả về toàn bộ danh sách phiên bản
        "versions": car.get("versions", []),
        "created_at": car.get("created_at"),
        "updated_at": car.get("updated_at"),
    }

@router.get("/", response_model=List[dict])
async def get_all_cars():
    """Lấy tất cả xe"""
    collection = get_collection("car_info")
    cars = []
    # Sắp xếp theo ngày tạo mới nhất
    async for car in collection.find().sort("created_at", -1):
        cars.append(car_helper(car))
    return cars

@router.get("/{car_id}", response_model=dict)
async def get_car_by_id(car_id: str):
    """Lấy chi tiết 1 xe"""
    if not ObjectId.is_valid(car_id):
        raise HTTPException(status_code=400, detail="Invalid car ID")
    
    collection = get_collection("car_info")
    car = await collection.find_one({"_id": ObjectId(car_id)})
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return car_helper(car)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_car(car: CarCreate):
    """Thêm xe mới"""
    collection = get_collection("car_info")
    
    # Kiểm tra trùng tên
    existing = await collection.find_one({"name": car.name})
    if existing:
        raise HTTPException(status_code=400, detail=f"Car '{car.name}' already exists")
    
    car_dict = car.model_dump()
    car_dict["created_at"] = datetime.utcnow()
    car_dict["updated_at"] = datetime.utcnow()
    
    result = await collection.insert_one(car_dict)
    new_car = await collection.find_one({"_id": result.inserted_id})
    
    return car_helper(new_car)

@router.put("/{car_id}", response_model=dict)
async def update_car(car_id: str, car: CarUpdate):
    """Cập nhật xe"""
    if not ObjectId.is_valid(car_id):
        raise HTTPException(status_code=400, detail="Invalid car ID")
    
    collection = get_collection("car_info")
    
    # Lọc bỏ các trường None để không ghi đè dữ liệu cũ bằng null
    update_data = {k: v for k, v in car.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    update_data["updated_at"] = datetime.utcnow()
    
    result = await collection.update_one(
        {"_id": ObjectId(car_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Car not found")
    
    updated_car = await collection.find_one({"_id": ObjectId(car_id)})
    return car_helper(updated_car)

@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: str):
    """Xóa xe"""
    if not ObjectId.is_valid(car_id):
        raise HTTPException(status_code=400, detail="Invalid car ID")
    
    collection = get_collection("car_info")
    result = await collection.delete_one({"_id": ObjectId(car_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Car not found")
    
    return None

@router.get("/search/{keyword}", response_model=List[dict])
async def search_cars(keyword: str):
    """Tìm kiếm xe theo tên hoặc nhãn YOLO"""
    collection = get_collection("car_info")
    cars = []
    
    # Tìm theo tên chính HOẶC tên trong danh sách yolo_labels
    query = {
        "$or": [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"yolo_labels": {"$regex": keyword, "$options": "i"}}
        ]
    }
    
    async for car in collection.find(query):
        cars.append(car_helper(car))
    
    return cars