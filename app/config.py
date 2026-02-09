import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")

    # ✅ Database Config (Local + Production Safe)
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Render sometimes gives postgres:// instead of postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        # Ensure SSL for Render Postgres
        if "sslmode=" not in DATABASE_URL:
            DATABASE_URL += "?sslmode=require"

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # ✅ Local fallback
        SQLALCHEMY_DATABASE_URI = "sqlite:///ecommerce.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt_dev_secret_change_me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000"))
    )

    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:5173"
    )

    # Uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
