import os
import sys
import requests
import asyncio
import random
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# 1. Cấu hình môi trường
# Load file .env từ thư mục backend
load_dotenv(Path(__file__).parent.parent / ".env")

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
# Lưu ý: Đảm bảo tên DB đúng với trong .env hoặc mặc định
DB_NAME = os.getenv("DB_NAME", "toyota_v2_db") 

# 2. Cấu hình đường dẫn lưu trữ
# Lưu vào: backend/datasets/retrain_data
BASE_DIR = Path(__file__).parent.parent
DATASET_DIR = BASE_DIR / "datasets" / "retrain_data"

# Tỷ lệ chia tập validation (0.2 nghĩa là 20% ảnh dùng để kiểm thử)
VAL_RATIO = 0.2 

async def download_image(url, save_path):
    """Hàm tải ảnh từ URL về máy"""
    try:
        # Giả lập User-Agent để tránh bị chặn bởi một số server
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f" Không tải được (Status {response.status_code}): {url}")
    except Exception as e:
        print(f" Lỗi tải {url}: {e}")
    return False

async def prepare_data_for_retraining():
    print(f" BẮT ĐẦU TẢI DỮ LIỆU ACTIVE LEARNING TỪ MONGODB...")
    print(f" Thư mục đích: {DATASET_DIR}")
    
    # Kết nối MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db["corrections"]

    # 1. Lấy dữ liệu đã được Admin duyệt (Approved)
    query = {"status": "approved"}
    total_approved = await collection.count_documents(query)
    
    if total_approved == 0:
        print(" Không tìm thấy dữ liệu 'approved'. Hãy vào Admin Dashboard duyệt các ảnh báo lỗi trước.")
        return

    print(f" Tìm thấy {total_approved} ảnh đã duyệt. Đang xử lý...")
    
    cursor = collection.find(query)
    count_success = 0
    count_exist = 0
    
    async for doc in cursor:
        try:
            # Lấy nhãn đúng (Actual Label)
            label = doc.get("actual_label")
            image_url = doc.get("image_url")
            doc_id = str(doc["_id"])

            if not label or not image_url:
                continue

            # 2. Quyết định xem ảnh này vào tập 'train' hay 'val'
            # Random 20% vào val, 80% vào train
            subset = "val" if random.random() < VAL_RATIO else "train"
            
            # 3. Tạo thư mục: datasets/retrain_data/train/{label}/
            label_dir = DATASET_DIR / subset / label
            label_dir.mkdir(parents=True, exist_ok=True)
            
            # Tên file
            filename = f"{label}_{doc_id}.jpg"
            save_path = label_dir / filename

            # 4. Tải ảnh
            if not save_path.exists():
                print(f"⬇ [{count_success + count_exist + 1}/{total_approved}] Tải về ({subset}): {label}/{filename}")
                if await download_image(image_url, save_path):
                    count_success += 1
            else:
                # print(f"Đã tồn tại: {filename}")
                count_exist += 1
                
        except Exception as e:
            print(f" Lỗi xử lý bản ghi {doc.get('_id')}: {e}")

    print("-" * 60)
    print(f" HOÀN TẤT!")
    print(f"   - Tải mới: {count_success}")
    print(f"   - Đã có sẵn: {count_exist}")
    print(f"   - Tổng cộng: {count_success + count_exist}/{total_approved}")
    print("-" * 60)
    
    # Hướng dẫn lệnh Train
    model_path = BASE_DIR / "app" / "car_classifier" / "best.pt"
    print(f" ĐỂ HUẤN LUYỆN LẠI (RETRAIN), HÃY CHẠY LỆNH SAU:")
    print(f"\n   yolo classify train data={DATASET_DIR} model={model_path} epochs=50 imgsz=640\n")

if __name__ == "__main__":
    # Fix lỗi EventLoop trên Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(prepare_data_for_retraining())
    except KeyboardInterrupt:
        print("\n Đã dừng bởi người dùng.")