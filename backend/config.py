import os
import ssl
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # =========================
    # EMAIL
    # =========================

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # =========================
    # DATABASE
    # =========================

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "sfpms_dev.db")
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "ssl": ssl._create_unverified_context()
        }
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # FRONTEND
    # =========================

    FRONTEND_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://172.16.18.87:5173",
        "https://sfpms-1.onrender.com"
    ]

    # =========================
    # UPLOADS
    # =========================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    # =========================
    # FILE SIZE
    # =========================

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # =========================
    # ALLOWED FILES
    # =========================

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "jpg",
        "jpeg",
        "png"
    }
