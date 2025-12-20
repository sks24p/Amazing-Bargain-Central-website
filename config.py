from pathlib import Path

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    # A secret key for sessions
    SECRET_KEY = "98WHz4FlyWFGERv4FfaJ"
    # This tells SQLAlchemy where to find/create my database file
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "abc_ecommerce.db"}'
    # This disables a feature that tracks modifications to objects
    # It is disabled because it uses extra memory and I don't need it
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME =  1800