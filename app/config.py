import os
from datetime import timedelta

class Config:
    """
    Konfigurasi dasar aplikasi EMOTIVA-MATH Backend
    """
    # Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'emotiva-math-secret-key-2024'
    DEBUG = True
    
    # CORS config
    CORS_HEADERS = 'Content-Type'
    
    # Database config
    # MySQL Configuration (Production)
    # Format: mysql+pymysql://username:password@host:port/database
    # Contoh: mysql+pymysql://root:password@localhost:3306/emotiva_math
    
    # Default MySQL settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'emotiva-math')
    
    # Construct MySQL URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI Engine config
    AI_MODEL_TYPE = 'rule-based'  # rule-based atau llm
    
    # Math Topic
    MATH_TOPIC = 'Bangun Ruang'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

# Default config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
