from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Dict, List

from app.db.mongo import get_collection
from app.services.car_service import car_service
from app.services.history_service import history_service

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/dashboard")
async def get_dashboard_stats():
    """
    Lấy tất cả thống kê cho dashboard
    """
    try:
        car_stats = await car_service.get_stats()
        history_stats = await history_service.get_stats()
        
        corrections_collection = get_collection("corrections")
        total_corrections = await corrections_collection.count_documents({})
        pending_corrections = await corrections_collection.count_documents({"status": "pending"})
        
        return {
            "cars": car_stats,
            "history": history_stats,
            "corrections": {
                "total": total_corrections,
                "pending": pending_corrections
            },
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_detection_timeline(days: int = 30):
    """
    Lấy timeline detections theo ngày (ĐÃ SỬA MÚI GIỜ VN)
    """
    try:
        collection = get_collection("history")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp",
                            "timezone": "+07:00" # <--- THÊM DÒNG NÀY (Quan trọng)
                        }
                    },
                    "count": {"$sum": 1},
                    "total_detections": {"$sum": {"$size": "$detections"}}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        timeline = []
        async for item in collection.aggregate(pipeline):
            timeline.append({
                "date": item["_id"],
                "uploads": item["count"],
                "detections": item["total_detections"]
            })
        
        return {
            "days": days,
            "timeline": timeline
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-cars")
async def get_top_detected_cars(limit: int = 10):
    """Lấy top xe được nhận diện nhiều nhất"""
    try:
        collection = get_collection("history")
        
        pipeline = [
            {"$unwind": "$detections"},
            {
                "$group": {
                    "_id": "$detections.class_name",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$detections.confidence"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        top_cars = []
        async for item in collection.aggregate(pipeline):
            top_cars.append({
                "car_name": item["_id"],
                "count": item["count"],
                "avg_confidence": round(item["avg_confidence"], 2)
            })
        
        return top_cars
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/car-types")
async def get_detection_by_car_type():
    """Thống kê detections theo loại xe"""
    try:
        history_collection = get_collection("history")
        cars_collection = get_collection("cars")
        
        car_types = {}
        async for car in cars_collection.find():
            car_types[car["name"]] = car.get("type", "Unknown")
        
        pipeline = [
            {"$unwind": "$detections"},
            {
                "$group": {
                    "_id": "$detections.class_name",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        type_stats = {}
        async for item in history_collection.aggregate(pipeline):
            car_name = item["_id"]
            car_type = car_types.get(car_name, "Unknown")
            
            if car_type not in type_stats:
                type_stats[car_type] = 0
            type_stats[car_type] += item["count"]
        
        result = [
            {"type": k, "count": v}
            for k, v in sorted(type_stats.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/confidence-distribution")
async def get_confidence_distribution():
    """Phân phối confidence"""
    try:
        collection = get_collection("history")
        
        pipeline = [
            {"$unwind": "$detections"},
            {
                "$bucket": {
                    "groupBy": "$detections.confidence",
                    "boundaries": [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    "default": "Other",
                    "output": {
                        "count": {"$sum": 1}
                    }
                }
            }
        ]
        
        distribution = []
        async for item in collection.aggregate(pipeline):
            range_start = item["_id"]
            distribution.append({
                "range": f"{range_start:.1f} - {range_start + 0.1:.1f}",
                "count": item["count"]
            })
        
        return distribution
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-activity")
async def get_hourly_activity():
    """
    Thống kê hoạt động theo giờ trong ngày (ĐÃ SỬA MÚI GIỜ VN)
    """
    try:
        collection = get_collection("history")
        
        pipeline = [
            {
                "$group": {
                    "_id": {
                        # Sửa cú pháp $hour để hỗ trợ timezone
                        "$hour": {
                            "date": "$timestamp",
                            "timezone": "+07:00" # <--- THÊM DÒNG NÀY
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        hourly = []
        async for item in collection.aggregate(pipeline):
            hourly.append({
                "hour": item["_id"],
                "count": item["count"]
            })
        
        return hourly
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))