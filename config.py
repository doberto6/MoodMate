import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///moodmate.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # App specific settings
    MAX_ENTRIES_PER_DAY = 5
    INSIGHTS_UPDATE_INTERVAL = 24  # hours

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
