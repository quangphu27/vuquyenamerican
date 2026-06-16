import os
from datetime import timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _db_name_from_uri(uri: str, default: str = "vuquyenamerican") -> str:
    """Lay ten database tu path trong MONGODB_URI, vi du .../vuquyenamerican"""
    if not uri:
        return default
    try:
        path = urlparse(uri).path.strip("/")
        if path:
            return path.split("/")[0]
    except Exception:
        pass
    return default


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/vuquyenamerican")
    MONGODB_DB = os.getenv("MONGODB_DB") or _db_name_from_uri(
        os.getenv("MONGODB_URI", ""), "vuquyenamerican"
    )

    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")
    CLOUDINARY_FOLDER_PREFIX = os.getenv("CLOUDINARY_FOLDER_PREFIX", "vuquyenamerican")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    CORS_ORIGINS = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    ]

    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200 per hour")
