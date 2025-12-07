import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "toyota_v2_db")

async def create_admin():
    print(" TẠO TÀI KHOẢN ADMIN")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    users = db["users"]
    
    email = "pdthanhf@gmail.com"  # Email thật của bạn
    password = input("Nhập mật khẩu đăng nhập web: ")
    
    hashed = pwd_context.hash(password)
    
    await users.update_one(
        {"email": email},
        {"$set": {"email": email, "password": hashed, "role": "admin"}},
        upsert=True
    )
    print(f" Đã tạo tài khoản Admin: {email}")

if __name__ == "__main__":
    asyncio.run(create_admin())