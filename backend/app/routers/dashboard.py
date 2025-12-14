from fastapi import APIRouter
from app.db.mongo import get_collection
from datetime import datetime, timedelta
import re 

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats():
    # --- CẤU HÌNH MẶC ĐỊNH ---
    stats = {
        "total_detections": 0,
        "avg_confidence": 0,
        "popular_cars": [],
        "detections_timeline": [],
        "detection_by_hour": [],
        "price_range_distribution": [],
    }
    
    try:
        col_history = get_collection("history")
        col_cars = get_collection("car_info")
        
        # Lấy 1000 dòng mới nhất
        raw_data = await col_history.find({}).sort("timestamp", -1).to_list(1000)
        
        total_dets = 0
        total_conf = 0.0
        conf_count = 0
        car_counts = {}
        
        date_map = {} 
        hour_counts = {i: 0 for i in range(24)}
        
        # Lấy thời gian hiện tại theo giờ Việt Nam (UTC + 7)
        now_vn = datetime.utcnow() + timedelta(hours=7)
        
        # Lọc 30 ngày gần nhất tính từ giờ VN
        time_window = now_vn - timedelta(days=30)

        for item in raw_data:
            ts = item.get("timestamp")
            
            # 1. Parse string ISO thành datetime object (nếu cần)
            if isinstance(ts, str):
                try: ts = datetime.fromisoformat(ts.replace("Z", ""))
                except: continue
            
            if not isinstance(ts, datetime): continue

            # 2. QUAN TRỌNG: Chuyển timestamp của bản ghi sang giờ VN ngay lập tức
            # (Giả sử DB lưu UTC, ta cộng 7 để ra giờ VN)
            ts_vn = ts + timedelta(hours=7)

            # 3. So sánh với time_window (đã là giờ VN)
            if ts_vn >= time_window:
                
                # --- XỬ LÝ TIMELINE ---
                # Vì ts_vn đã là giờ Việt Nam, nên hàm strftime sẽ ra đúng ngày 15/12
                date_key = ts_vn.strftime("%Y-%m-%d") 
                display_label = ts_vn.strftime("%d/%m")
                
                detections = item.get("detections", [])
                det_count = len(detections)
                
                if date_key not in date_map:
                    date_map[date_key] = {"date": display_label, "detections": 0}
                
                date_map[date_key]["detections"] += det_count
                
                # --- XỬ LÝ GIỜ (DETECTION BY HOUR) ---
                # Vì ts_vn đã cộng 7 rồi, nên chỉ cần lấy .hour là xong
                # Không cần công thức (h+7)%24 phức tạp nữa
                local_hour = ts_vn.hour
                hour_counts[local_hour] += det_count

                # --- CHI TIẾT XE ---
                for d in detections:
                    total_dets += 1
                    name = d.get("class_name") or d.get("label") or "Unknown"
                    car_counts[name] = car_counts.get(name, 0) + 1
                    conf = d.get("confidence", 0)
                    if conf:
                        total_conf += float(conf)
                        conf_count += 1

        # ======================================================
        # TỔNG HỢP KẾT QUẢ
        # ======================================================
        
        # 1. Timeline
        sorted_keys = sorted(date_map.keys()) 
        stats["detections_timeline"] = [
            {"date": date_map[k]["date"], "detections": date_map[k]["detections"]} 
            for k in sorted_keys
        ]
        
        # 2. Top Cars
        sorted_cars = sorted(car_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        stats["popular_cars"] = [{"car_name": k, "count": v} for k, v in sorted_cars]
        
        # 3. Hourly
        stats["detection_by_hour"] = [{"hour": f"{h}:00", "count": hour_counts[h]} for h in range(24)]

        # 4. Summary
        stats["total_detections"] = total_dets
        if conf_count > 0:
            stats["avg_confidence"] = round(total_conf / conf_count, 4)

        # 5. Price Distribution (Logic này giữ nguyên vì không liên quan thời gian)
        all_cars = await col_cars.find({}).to_list(None)
        price_dist = {'Dưới 500 triệu': 0, '500-800 triệu': 0, '800-1.2 tỷ': 0, 'Trên 1.2 tỷ': 0}
        
        for car in all_cars:
            versions = car.get("versions", [])
            for ver in versions:
                price_str = ver.get("price", "0")
                try:
                    price_clean = re.sub(r'\D', '', str(price_str))
                    if not price_clean: continue
                    price = int(price_clean)
                    if price < 500000000: price_dist['Dưới 500 triệu'] += 1
                    elif price < 800000000: price_dist['500-800 triệu'] += 1
                    elif price < 1200000000: price_dist['800-1.2 tỷ'] += 1
                    else: price_dist['Trên 1.2 tỷ'] += 1
                except: continue

        stats["price_range_distribution"] = [{"name": k, "value": v} for k, v in price_dist.items()]

        return stats

    except Exception as e:
        print(f"Error stats: {e}")
        return stats