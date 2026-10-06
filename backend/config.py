import os
import ssl
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================
    # SECRET KEY
    # =========================

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "sfpms-development-secret-key-change-in-production"
    )

    # =========================
    # EMAIL
    # =========================

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # =========================
    # DATABASE
    # =========================

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "sfpms_dev.db")
    )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    # SQLite does NOT support the MySQL SSL argument.
    # MySQL/Aiven can use SSL.
    if DATABASE_URL.startswith("mysql"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "ssl": {
                    "ca": os.getenv("MYSQL_SSL_CA", "")
                }
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # FRONTEND
    # =========================

    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://localhost:5174"
        ).split(",")
        if origin.strip()
    ]

    # =========================
    # UPLOADS
    # =========================

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "doc",
        "docx"
    }
