"""
GUVNL Queue Management System - Configuration Settings
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://guvnl_user:guvnl_password@localhost:5432/guvnl_queue_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CELERY_ENABLE_UTC = True
    
    # Twilio SMS
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Email
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Firebase (for push notifications)
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
    
    # Application Settings
    MAX_APPOINTMENTS_PER_DAY = int(os.environ.get('MAX_APPOINTMENTS_PER_DAY', 100))
    DEFAULT_APPOINTMENT_DURATION = int(os.environ.get('DEFAULT_APPOINTMENT_DURATION', 30))
    QUEUE_ADVANCE_BOOKING_DAYS = int(os.environ.get('QUEUE_ADVANCE_BOOKING_DAYS', 30))
    NOTIFICATION_ADVANCE_MINUTES = int(os.environ.get('NOTIFICATION_ADVANCE_MINUTES', 15))
    
    # Security
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    
    # Office Configuration
    DEFAULT_OFFICE_NAME = os.environ.get('DEFAULT_OFFICE_NAME', 'GUVNL Head Office')
    DEFAULT_OFFICE_ADDRESS = os.environ.get('DEFAULT_OFFICE_ADDRESS', 'Vadodara, Gujarat, India')
    DEFAULT_OFFICE_PHONE = os.environ.get('DEFAULT_OFFICE_PHONE', '+91-265-2355501')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Enable SQL query logging in development
    SQLALCHEMY_ECHO = True
    
    # Less strict CORS for development
    CORS_ORIGINS = 'http://localhost:3000,http://localhost:3001'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Production database with connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 20,
        'max_overflow': 30,
    }
    
    # Stricter CORS in production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF tokens in forms for testing
    WTF_CSRF_ENABLED = False
    
    # Use a separate Redis database for testing
    REDIS_URL = 'redis://localhost:6379/1'
    
    # Short token expiry for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=10)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}