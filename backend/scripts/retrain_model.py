import os
import shutil
import glob
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime

# --- CẤU HÌNH ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "datasets" / "retrain_data" # Nơi chứa ảnh đã tải về
MODEL_DIR = BASE_DIR / "app" / "car_classifier"
CURRENT_MODEL_PATH = MODEL_DIR / "best.pt"

# --- CẤU HÌNH TRAIN ---
EPOCHS = 20        # Số vòng lặp (Để test thì để nhỏ, thực tế nên để 50-100)
IMG_SIZE = 640     # Kích thước ảnh (phải khớp model cũ)
BATCH_SIZE = 16    # Tùy chỉnh theo RAM của bạn

def retrain():
    print(" BẮT ĐẦU QUÁ TRÌNH HUẤN LUYỆN LẠI (RETRAIN)...")

    # 1. Kiểm tra dữ liệu
    if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
        print(" Lỗi: Không tìm thấy dữ liệu train tại", DATA_DIR)
        print("👉 Hãy chạy 'python scripts/prepare_dataset.py' trước!")
        return

    # 2. Load model hiện tại để fine-tune (học tiếp)
    print(f" Đang tải model cũ từ: {CURRENT_MODEL_PATH}")
    if not CURRENT_MODEL_PATH.exists():
        print("⚠️ Không tìm thấy model cũ. Sẽ train từ đầu (yolov8n-cls.pt)...")
        model = YOLO('yolov8n-cls.pt') # Fallback nếu chưa có best.pt
    else:
        model = YOLO(str(CURRENT_MODEL_PATH))

    # 3. Bắt đầu Train
    print("🔥 Đang train... (Vui lòng chờ, có thể mất vài phút)")
    try:
        # Train model
        results = model.train(
            data=str(DATA_DIR),
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            project=str(BASE_DIR / "runs" / "classify"), # Lưu kết quả vào folder runs
            name="retrain_session",
            exist_ok=True # Ghi đè folder retrain_session cũ để không tạo rác
        )
        print("Train hoàn tất!")
    except Exception as e:
        print(f" Lỗi trong quá trình train: {e}")
        return

    # 4. Tìm và Cập nhật Model mới
    # YOLO thường lưu model ở: runs/classify/retrain_session/weights/best.pt
    new_model_path = BASE_DIR / "runs" / "classify" / "retrain_session" / "weights" / "best.pt"

    if new_model_path.exists():
        print(" Đang cập nhật model mới cho hệ thống...")
        
        # Backup model cũ (thêm ngày giờ vào tên)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = MODEL_DIR / f"best_backup_{timestamp}.pt"
        if CURRENT_MODEL_PATH.exists():
            shutil.move(str(CURRENT_MODEL_PATH), str(backup_path))
            print(f"   -> Đã backup model cũ thành: {backup_path.name}")

        # Copy model mới vào vị trí chính thức
        shutil.copy(str(new_model_path), str(CURRENT_MODEL_PATH))
        print(f" ĐÃ CẬP NHẬT: {CURRENT_MODEL_PATH}")
        print(" Hệ thống đã thông minh hơn! Vui lòng khởi động lại Backend để áp dụng.")
    else:
        print("Không tìm thấy file model mới sau khi train.")

if __name__ == "__main__":
    retrain()