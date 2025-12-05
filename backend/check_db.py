import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.mongo import MongoDB, get_collection
from app.core.config import settings

async def check():
    print("⏳ Đang khởi tạo kết nối Database thủ công...")
    
    # --- BƯỚC SỬA LỖI: TỰ KẾT NỐI MONGODB ---
    # Kiểm tra xem biến config của bạn tên là MONGODB_URI hay MONGODB_URL
    # Thường là settings.MONGODB_URI hoặc settings.MONGODB_URL
    try:
        conn_str = getattr(settings, "MONGODB_URI", getattr(settings, "MONGODB_URL", None))
        if not conn_str:
            print("❌ Không tìm thấy biến MONGODB_URI trong settings. Hãy kiểm tra file config.")
            return

        MongoDB.client = AsyncIOMotorClient(conn_str)
        print("✅ Kết nối thành công!")
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")
        return
    # ----------------------------------------

    col = get_collection("history")
    
    # 1. Kiểm tra có dữ liệu không
    count = await col.count_documents({})
    print(f"👉 Tổng số documents trong history: {count}")
    
    if count == 0:
        print("⚠️ Database trống! Hãy nhận diện thử vài ảnh trên web trước.")
        return

    # 2. Lấy thử 1 dòng mới nhất xem cấu trúc
    latest = await col.find_one(sort=[("timestamp", -1)])
    
    if latest:
        print("\n👉 Cấu trúc dòng mới nhất:")
        print(f"- ID: {latest.get('_id')}")
        
        ts = latest.get('timestamp')
        print(f"- Timestamp: {ts} (Kiểu dữ liệu: {type(ts)})")
        
        if isinstance(ts, str):
            print("🔴 CẢNH BÁO: Timestamp đang lưu dạng STRING. Đây là lý do biểu đồ không chạy!")
        else:
            print("🟢 Timestamp chuẩn (Datetime).")

        detections = latest.get('detections', [])
        print(f"- Số xe trong mảng detections: {len(detections)}")
        
        if detections:
            print(f"- Chi tiết xe đầu tiên: {detections[0]}")
            # Kiểm tra tên trường chứa tên xe
            keys = detections[0].keys()
            print(f"- Các trường có trong detection: {list(keys)}")
            if 'class_name' in keys:
                print("🟢 Có trường 'class_name'.")
            else:
                print("🔴 Thiếu trường 'class_name'. Biểu đồ Top xe sẽ bị lỗi.")

if __name__ == "__main__":
    # Sửa lỗi event loop trên Windows nếu cần
    try:
        asyncio.run(check())
    except RuntimeError: # Fix cho Windows nếu loop bị đóng
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(check())