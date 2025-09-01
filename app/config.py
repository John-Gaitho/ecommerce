import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://ecommerce_user:strongpassword@localhost:5432/ecommerce_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_dev_secret_change_me")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000"))

    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "https://199adc73-7161-4f4c-83fc-a98266f4366f.lovableproject.com",
    )

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB

    # M-Pesa Daraja
    MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://example.com/api/mpesa/callback")
