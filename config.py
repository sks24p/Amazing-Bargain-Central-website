from pathlib import Path
from dotenv import load_dotenv
import os

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv()
    # Secret key for session encryption and signing
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Database

    # This tells SQLAlchemy where to find/create my database file
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "abc_ecommerce.db"}'
    # This disables a feature that tracks modifications to objects
    # It is disabled because it uses extra memory and I don't need it
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF Protection
    WTF_CSRF_ENABLED = True

    # File upload security
    UPLOAD_FOLDER_REVIEWS = Path('static/uploads/reviews')
    UPLOAD_FOLDER_PRODUCTS = Path('static/uploads/products')
    MAX_FILE_SIZE = 5 * 1024 * 1024

    # Session cookies (essential for security)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME =  1800