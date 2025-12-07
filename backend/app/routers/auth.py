from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random
from app.db.mongo import get_collection
from app.utils.security import verify_password, create_access_token
from app.utils.email_utils import send_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

@router.post("/login")
async def login_step1(data: LoginRequest):
    users = get_collection("users")
    user = await users.find_one({"email": data.email})
    
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Email hoặc mật khẩu không đúng")

    # Sinh OTP ngẫu nhiên
    otp_code = f"{random.randint(100000, 999999)}"
    
    # Lưu OTP vào DB
    await users.update_one(
        {"email": data.email},
        {"$set": {
            "otp": otp_code,
            "otp_expiry": datetime.utcnow() + timedelta(minutes=5)
        }}
    )
    
    # Gửi Email
    try:
        await send_otp_email(data.email, otp_code)
    except Exception as e:
        print(f"Lỗi gửi mail: {e}")
        raise HTTPException(status_code=500, detail="Lỗi gửi email xác thực")

    return {"message": "OTP sent", "email": data.email}

@router.post("/verify-otp")
async def login_step2(data: OTPVerifyRequest):
    users = get_collection("users")
    user = await users.find_one({"email": data.email})
    
    if not user:
        raise HTTPException(status_code=400, detail="User không tồn tại")

    if not user.get("otp") or user.get("otp") != data.otp:
        raise HTTPException(status_code=400, detail="Mã OTP sai")
        
    if datetime.utcnow() > user.get("otp_expiry"):
        raise HTTPException(status_code=400, detail="Mã OTP đã hết hạn")

    # Xóa OTP sau khi dùng và cấp Token
    await users.update_one({"email": data.email}, {"$unset": {"otp": "", "otp_expiry": ""}})
    token = create_access_token({"sub": user["email"], "role": "admin"})
    
    return {"access_token": token, "token_type": "bearer"}