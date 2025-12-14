import os
import shutil
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime

# --- CẤU HÌNH ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datasets" / "retrain_data"
MODEL_DIR = BASE_DIR / "app" / "car_classifier"

# Tên model vệ tinh (Bộ não phụ)
CORRECTION_MODEL_PATH = MODEL_DIR / "correction.pt"

# --- CẤU HÌNH TRAIN ---
EPOCHS = 30           # Học kỹ một chút vì ít ảnh
IMG_SIZE = 640
BATCH_SIZE = 16

def retrain():
    print("="*60)
    print(" 🛠️  HUẤN LUYỆN MÔ HÌNH VỆ TINH (CORRECTION MODEL)")
    print("="*60)

    # 1. Kiểm tra dữ liệu
    if not DATA_DIR.exists():
        print(f"❌ Lỗi: Không tìm thấy thư mục {DATA_DIR}")
        return

    # 2. Load Model Vệ tinh
    # Luôn ưu tiên load model correction cũ để học tiếp (nếu có)
    if CORRECTION_MODEL_PATH.exists():
        print(f"⬇️ Đang tải model vệ tinh hiện tại để cập nhật: {CORRECTION_MODEL_PATH}")
        model = YOLO(str(CORRECTION_MODEL_PATH))
    else:
        print("🆕 Chưa có model vệ tinh. Tạo mới từ yolov8n-cls.pt...")
        model = YOLO('yolov8n-cls.pt') # Bắt buộc dùng bản -cls (Classification)

    # 3. Train (Bắt buộc task='classify')
    print(f"🚀 Đang học dữ liệu mới từ {DATA_DIR}...")
    try:
        results = model.train(
            data=str(DATA_DIR),
            task='classify',      
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            project=str(BASE_DIR / "runs" / "classify"),
            name="correction_session",
            exist_ok=True
        )
        print("✅ Train hoàn tất!")
    except Exception as e:
        print(f"❌ Lỗi khi train: {e}")
        return

    # 4. Lưu model
    new_weights = BASE_DIR / "runs" / "classify" / "correction_session" / "weights" / "best.pt"

    if new_weights.exists():
        print("🔄 Đang cập nhật file correction.pt...")
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(new_weights), str(CORRECTION_MODEL_PATH))
        print(f"✅ THÀNH CÔNG! Đã lưu model sửa lỗi tại: {CORRECTION_MODEL_PATH}")
    else:
        print("❌ Lỗi: Không tìm thấy file weights sau khi train.")

if __name__ == "__main__":
    retrain()