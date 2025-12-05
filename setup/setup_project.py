import os

# Tên thư mục gốc
root_dir = "TOYOTAV2"

# Danh sách tất cả các file cần tạo
files = [
    # Backend
    "backend/app/__init__.py",
    "backend/app/car_classifier/best.pt",
    "backend/app/car_classifier/class_info.json",
    "backend/app/car_classifier/inference.py",
    "backend/app/car_classifier/preprocess.py",
    "backend/app/core/__init__.py",
    "backend/app/core/config.py",
    "backend/app/db/__init__.py",
    "backend/app/db/mongo.py",
    "backend/app/models/__init__.py",
    "backend/app/models/car.py",
    "backend/app/models/history.py",
    "backend/app/models/correct.py",
    "backend/app/routers/__init__.py",
    "backend/app/routers/cars.py",
    "backend/app/routers/detect.py",
    "backend/app/routers/history.py",
    "backend/app/routers/correct.py",
    "backend/app/routers/stats.py",
    "backend/app/services/__init__.py",
    "backend/app/services/detection_service.py",
    "backend/app/services/car_service.py",
    "backend/app/services/history_service.py",
    "backend/app/utils/__init__.py",
    "backend/app/utils/cloudinary_utils.py",
    "backend/app/.env",
    "backend/app/main.py",
    "backend/app/requirements.txt",
    "backend/app/start.sh",
    "backend/app/start.bat",

    # Frontend
    "frontend/public/favicon.ico",
    "frontend/src/api/index.js",
    "frontend/src/components/admin/AdminDashboard.jsx",
    "frontend/src/components/common/Navbar.jsx",
    "frontend/src/components/detector/ImageUpload.jsx",
    "frontend/src/components/detector/DetectionResult.jsx",
    "frontend/src/components/detector/SpecsTable.jsx",
    "frontend/src/components/history/HistoryView.jsx",
    "frontend/src/constants/mockData.js",
    "frontend/src/App.jsx",
    "frontend/src/App.css",
    "frontend/src/main.jsx",
    "frontend/src/index.css",
    "frontend/.env",
    "frontend/.gitignore",
    "frontend/index.html",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/tailwind.config.js",
    "frontend/postcss.config.js",
    "frontend/start.sh",

    # Root files
    "README.md"
]

def create_structure():
    print(f"🚀 Đang khởi tạo cấu trúc dự án: {root_dir}...")
    
    for file_path in files:
        # Ghép đường dẫn đầy đủ
        full_path = os.path.join(root_dir, file_path)
        
        # Tạo thư mục chứa file (nếu chưa có)
        dir_name = os.path.dirname(full_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            
        # Tạo file rỗng
        if not os.path.exists(full_path):
            with open(full_path, 'w', encoding='utf-8') as f:
                pass # Chỉ tạo file rỗng
    
    print("✅ Đã tạo xong toàn bộ cấu trúc thư mục và file!")
    print(f"👉 Hãy mở thư mục '{root_dir}' trong VS Code để bắt đầu code.")

if __name__ == "__main__":
    create_structure()