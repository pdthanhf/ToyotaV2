from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongo import MongoDB
# Import các router hiện có của bạn
from app.routers import cars, detect, history, correct, stats, dashboard, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await MongoDB.connect()
    yield
    # Shutdown
    await MongoDB.close()

# Create FastAPI app
app = FastAPI(
    title="Toyota Computer Vision API",
    description="API nhận diện và quản lý thông tin xe Toyota",
    version="2.0.0",
    lifespan=lifespan
)

# --- CẤU HÌNH CORS (Đã gộp và tối ưu) ---
# Kết hợp cả settings và hardcode localhost để đảm bảo frontend chạy được ngay
origins = settings.CORS_ORIGINS if hasattr(settings, "CORS_ORIGINS") else []
origins.extend([
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # React default
    "*"                       # Cho phép tất cả (Dùng khi dev, nên tắt khi production)
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Sử dụng danh sách origins đã gộp
    allow_credentials=True,
    allow_methods=["*"],    # Cho phép tất cả: GET, POST...
    allow_headers=["*"],
)

# --- INCLUDE ROUTERS  ---
app.include_router(cars.router, prefix="/api")
app.include_router(detect.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(correct.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

# --- ROOT & HEALTH CHECK ---
@app.get("/")
async def root():
    return {
        "message": "Toyota CV2 API is running",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )