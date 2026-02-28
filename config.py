# config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

class Config:
    # Secret key for sessions and CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    # CSRF Protection Settings
    WTF_CSRF_ENABLED = True  # Enable CSRF protection
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', os.urandom(24).hex())
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF token valid for 1 hour
    WTF_CSRF_SSL_STRICT = True  # Strict SSL checking
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']  # Methods to protect
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{INSTANCE_DIR / "database.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folders
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False 
    # In development, you might want to disable CSRF for testing
    # WTF_CSRF_ENABLED = False  # Uncomment for testing only

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Stronger CSRF settings for production
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutes
    WTF_CSRF_SSL_STRICT = True
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Use environment variables for secrets
    SECRET_KEY = os.getenv('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}