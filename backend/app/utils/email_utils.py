import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
# from dotenv import load_dotenv  <-- Tạm thời comment dòng này lại
from pathlib import Path

# --- CẤU HÌNH CỨNG (HARDCODE) ĐỂ CHẠY NGAY ---
# Bỏ qua việc đọc .env, điền trực tiếp vào đây
MAIL_USERNAME = "pdthanhf@gmail.com"
MAIL_PASSWORD = "ygrwffzskfphdxnk"
MAIL_FROM = "pdthanhf@gmail.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.gmail.com"

print(f"📧 ĐANG DÙNG CẤU HÌNH CỨNG: {MAIL_USERNAME}")

# Cấu hình kết nối
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_otp_email(email_to: str, otp_code: str):
    """Gửi mã OTP qua email"""
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #d32f2f;">Toyota Admin Security</h2>
        <p>Xin chào Admin,</p>
        <p>Mã xác nhận đăng nhập của bạn là:</p>
        <h1 style="background-color: #f5f5f5; padding: 10px; text-align: center; letter-spacing: 5px; color: #333;">{otp_code}</h1>
        <p>Mã này có hiệu lực trong <strong>5 phút</strong>.</p>
    </div>
    """

    message = MessageSchema(
        subject="[ToyotaAdmin] Mã xác nhận đăng nhập",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)