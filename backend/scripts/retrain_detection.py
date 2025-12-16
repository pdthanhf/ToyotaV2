import os
import shutil
import requests
import yaml
import json
from pathlib import Path
from pymongo import MongoClient
from ultralytics import YOLO
from datetime import datetime
from PIL import Image

# --- CẤU HÌNH ĐƯỜNG DẪN ---
CURRENT_FILE = Path(__file__).resolve()

# Tìm thư mục gốc TOYOTAV2
temp_path = CURRENT_FILE
while temp_path.name != 'backend' and temp_path.parent != temp_path:
    temp_path = temp_path.parent
if temp_path.name == 'backend':
    BASE_DIR = temp_path.parent
else:
    BASE_DIR = CURRENT_FILE.parent.parent.parent

# Cấu hình Dataset
DATASET_ROOT = BASE_DIR / "dataset" 
NEW_DATA_DIR = DATASET_ROOT / "new_data"
YAML_PATH = DATASET_ROOT / "data.yaml"

# --- SỬA ĐỔI 1: Đưa folder runs vào trong dataset cho gọn ---
RUNS_DIR = DATASET_ROOT / "runs"

# Đường dẫn Model
CLASSIFIER_DIR = BASE_DIR / "backend" / "app" / "car_classifier"
MODEL_PATH = CLASSIFIER_DIR / "best.pt"
BACKUP_PATH = CLASSIFIER_DIR / "best_backup.pt"

# MongoDB Config
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "toyota_v2_db"
COLLECTION_NAME = "corrections"

# Params
EPOCHS = 50
IMG_SIZE = 640
BATCH_SIZE = 8

def setup_directories():
    """Chỉ dọn dẹp folder new_data. KHÔNG đụng vào original_data."""
    if not DATASET_ROOT.exists():
        print(f" Lỗi: Không tìm thấy thư mục dataset gốc tại: {DATASET_ROOT}")
        return False

    dirs = [
        NEW_DATA_DIR / "train" / "images",
        NEW_DATA_DIR / "train" / "labels",
        NEW_DATA_DIR / "val" / "images",
        NEW_DATA_DIR / "val" / "labels"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    print(f" Đang dọn dẹp dữ liệu tạm trong: {NEW_DATA_DIR.name} ...")
    def clean_folder(folder_path):
        if folder_path.exists():
            for f in folder_path.glob("*"):
                try: 
                    if f.is_file(): os.remove(f)
                except: pass

    clean_folder(NEW_DATA_DIR / "train" / "images")
    clean_folder(NEW_DATA_DIR / "train" / "labels")
    clean_folder(NEW_DATA_DIR / "val" / "images")
    clean_folder(NEW_DATA_DIR / "val" / "labels")
    
    print(" Đã dọn dẹp xong folder tạm.")
    return True

def load_classes_from_yaml():
    if not YAML_PATH.exists():
        return {}
    try:
        with open(YAML_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            names = data.get('names', {})
            if isinstance(names, list):
                return {v: i for i, v in enumerate(names)}
            elif isinstance(names, dict):
                return {v: k for k, v in names.items()}
            return {}
    except: return {}

def create_yolo_label(model, image_path, correct_label_name, class_map, output_path):
    try:
        results = model.predict(image_path, conf=0.1, verbose=False)
        if not results or len(results[0].boxes) == 0:
            return False

        best_box = results[0].boxes[0]
        x, y, w, h = best_box.xywhn[0].tolist()
        
        if correct_label_name not in class_map: return False
        correct_class_id = class_map[correct_label_name]

        with open(output_path, 'w') as f:
            f.write(f"{correct_class_id} {x} {y} {w} {h}\n")
        return True
    except: return False

def prepare_data():
    print(" Đang tải dữ liệu MỚI từ MongoDB...")
    if not setup_directories(): return 0
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    current_model = YOLO(str(MODEL_PATH))
    class_map = load_classes_from_yaml()
    if not class_map: return 0
    
    cursor = collection.find({"status": "approved", "is_retrained": {"$ne": True}})
    
    count = 0
    for item in cursor:
        img_url = item.get("image_url") 
        correct_label = item.get("actual_label")
        if not img_url or not correct_label: continue

        file_id = str(item["_id"])
        img_save_path = NEW_DATA_DIR / "train" / "images" / f"{file_id}.jpg"
        
        try:
            resp = requests.get(img_url)
            if resp.status_code == 200:
                with open(img_save_path, 'wb') as f: f.write(resp.content)
            else: continue
        except: continue

        txt_save_path = NEW_DATA_DIR / "train" / "labels" / f"{file_id}.txt"
        if create_yolo_label(current_model, img_save_path, correct_label, class_map, txt_save_path):
            count += 1
        else:
            if img_save_path.exists(): os.remove(img_save_path)

    # Copy val (20%)
    files = list((NEW_DATA_DIR / "train" / "images").glob("*.jpg"))
    num_val = max(1, int(len(files) * 0.2)) 
    for i, f in enumerate(files):
        if i < num_val:
            shutil.copy(f, NEW_DATA_DIR / "val" / "images" / f.name)
            txt_name = f.stem + ".txt"
            src_txt = NEW_DATA_DIR / "train" / "labels" / txt_name
            if src_txt.exists():
                shutil.copy(src_txt, NEW_DATA_DIR / "val" / "labels" / txt_name)

    print(f" Đã tải xong {count} ảnh mới.")
    return count

def retrain_main():
    if not MODEL_PATH.exists():
        print(f" Không tìm thấy model tại {MODEL_PATH}")
        return

    count = prepare_data()
    if count == 0:
        print(" Không có ảnh mới. Hệ thống sẽ train lại trên dữ liệu gốc.")

    shutil.copy(MODEL_PATH, BACKUP_PATH)
    print(f" Đã backup model cũ.")

    print(f" Bắt đầu Train...")
    try:
        model = YOLO(str(MODEL_PATH))
        
        results = model.train(
            data=str(YAML_PATH),
            epochs=EPOCHS,
            imgsz=IMG_SIZE,
            batch=BATCH_SIZE,
            project=str(RUNS_DIR / "detect"),
            # --- SỬA ĐỔI 2: Đổi tên thành 'train' cho gọn (bỏ chữ finetune) ---
            name="train", 
            exist_ok=True,
            device='cpu' 
        )
        
        print(" Train hoàn tất!")
        
        new_weights = RUNS_DIR / "detect" / "train" / "weights" / "best.pt"
        
        if new_weights.exists():
            shutil.copy(str(new_weights), str(MODEL_PATH))
            print(" Đã update best.pt")
            
            client = MongoClient(MONGO_URI)
            client[DB_NAME][COLLECTION_NAME].update_many(
                {"status": "approved", "is_retrained": {"$ne": True}},
                {"$set": {"is_retrained": True, "retrained_at": datetime.now()}}
            )
            print(" Đã cập nhật trạng thái MongoDB.")
        else:
            print(f" Lỗi: Không thấy file weights mới tại {new_weights}")

    except Exception as e:
        print(f" Lỗi Fatal: {e}")
        if BACKUP_PATH.exists():
            shutil.copy(BACKUP_PATH, MODEL_PATH)
            print("Đã khôi phục model cũ.")

if __name__ == "__main__":
    retrain_main()