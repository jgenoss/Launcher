import os
from datetime import timedelta

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///launcher_admin.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    ALLOWED_EXTENSIONS = {
        'update': {'zip'},
        'launcher': {'exe'},
        'file': {'exe', 'dll', 'txt', 'xml', 'json', 'png', 'jpg', 'gif'},
        'banner': {'html', 'htm'}
    }
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'launcher_admin.log'
    
    # Configuración de la API
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100 per hour'
    API_CORS_ORIGINS = os.environ.get('API_CORS_ORIGINS', '*').split(',')
    
    # Configuración del launcher
    LAUNCHER_URL_BASE = os.environ.get('LAUNCHER_URL_BASE') or 'http://localhost:5000/Launcher'
    LAUNCHER_CHECK_INTERVAL = int(os.environ.get('LAUNCHER_CHECK_INTERVAL', '300'))  # 5 minutos
    
    # Configuración de backup
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', '3600'))  # 1 hora
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
    
    # Configuración de notificaciones
    NOTIFICATION_ENABLED = os.environ.get('NOTIFICATION_ENABLED', 'False').lower() == 'true'
    NOTIFICATION_WEBHOOK_URL = os.environ.get('NOTIFICATION_WEBHOOK_URL')
    
    # Configuración de seguridad
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https:",
        'connect-src': "'self'"
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    WTF_CSRF_ENABLED = False  # Deshabilitado para desarrollo
    SQLALCHEMY_ECHO = False  # True para ver queries SQL

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    FORCE_HTTPS = True
    
    # En producción, estas variables deben estar en el entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY debe estar configurada en producción")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL debe estar configurada en producción")

class TestingConfig(Config):
    """Configuración para tests"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = 'test_uploads'

# Configuración por defecto según el entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])