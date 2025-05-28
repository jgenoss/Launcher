#!/usr/bin/env python3
"""
Script de inicio para Launcher Admin Panel
Configura y ejecuta la aplicación Flask con todas las configuraciones necesarias
"""

import os
import sys
import logging
from datetime import datetime
from werkzeug.serving import WSGIRequestHandler
from app import app, db, create_admin_user

def setup_logging():
    """Configurar sistema de logging"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'launcher_admin_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar logger específico para la aplicación
    app.logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

def check_environment():
    """Verificar variables de entorno y configuración"""
    logger = logging.getLogger(__name__)
    
    # Verificar variables críticas
    critical_vars = ['SECRET_KEY']
    missing_vars = []
    
    for var in critical_vars:
        if not os.environ.get(var) and not getattr(app.config, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        logger.warning("Usando valores por defecto (no recomendado para producción)")
    
    # Verificar directorios necesarios
    directories = [
        'uploads',
        'uploads/files',
        'uploads/updates', 
        'static/downloads',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directorio verificado: {directory}")
    
    return True

def initialize_database():
    """Inicializar base de datos"""
    logger = logging.getLogger(__name__)
    
    try:
        with app.app_context():
            # Crear tablas si no existen
            db.create_all()
            logger.info("Base de datos inicializada correctamente")
            
            # Crear usuario administrador por defecto
            #create_admin_user()
            
            return True
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        return False

def run_development():
    """Ejecutar en modo desarrollo"""
    logger = logging.getLogger(__name__)
    logger.info("Iniciando servidor de desarrollo...")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True,
        threaded=True
    )

def run_production():
    """Ejecutar en modo producción"""
    logger = logging.getLogger(__name__)
    logger.info("Iniciando servidor de producción...")
    
    try:
        # Importar gunicorn solo si está disponible
        from gunicorn.app.wsgiapp import WSGIApplication
        
        class GunicornApp(WSGIApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()
            
            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)
            
            def load(self):
                return self.application
        
        options = {
            'bind': f"0.0.0.0:{os.environ.get('PORT', 5000)}",
            'workers': int(os.environ.get('WORKERS', 4)),
            'worker_class': 'sync',
            'worker_connections': 1000,
            'timeout': 30,
            'keepalive': 2,
            'max_requests': 1000,
            'max_requests_jitter': 100,
            'access_logfile': 'logs/access.log',
            'error_logfile': 'logs/error.log',
            'loglevel': 'info',
            'capture_output': True
        }
        
        GunicornApp(app, options).run()
        
    except ImportError:
        logger.warning("Gunicorn no está disponible, usando servidor de desarrollo")
        logger.warning("Para producción, instala gunicorn: pip install gunicorn")
        run_development()

def show_banner():
    """Mostrar banner de inicio"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    LAUNCHER ADMIN PANEL                     ║
║                                                              ║
║  🎮 Panel de administración completo para launcher          ║
║  📁 Gestión de archivos y versiones                         ║
║  📊 Estadísticas y logs en tiempo real                      ║
║  🔐 Sistema de autenticación seguro                         ║
║                                                              ║
║  Desarrollado para gestionar actualizaciones de juegos      ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_startup_info():
    """Mostrar información de inicio"""
    logger = logging.getLogger(__name__)
    
    env = os.environ.get('FLASK_ENV', 'development')
    port = os.environ.get('PORT', 5000)
    host = '0.0.0.0'
    
    logger.info(f"Entorno: {env}")
    logger.info(f"Puerto: {port}")
    logger.info(f"Host: {host}")
    
    if env == 'development':
        logger.info(f"URL de acceso: http://localhost:{port}")
        logger.info(f"URL de la API: http://localhost:{port}/api")
        logger.info("Credenciales por defecto: admin / admin123")
    
    logger.info("Presiona Ctrl+C para detener el servidor")

def main():
    """Función principal"""
    try:
        # Mostrar banner
        show_banner()
        
        # Configurar logging
        logger = setup_logging()
        logger.info("Iniciando Launcher Admin Panel...")
        
        # Verificar entorno
        if not check_environment():
            logger.error("Error en la verificación del entorno")
            sys.exit(1)
        
        # Inicializar base de datos
        if not initialize_database():
            logger.error("Error inicializando base de datos")
            sys.exit(1)
        
        # Mostrar información de inicio
        show_startup_info()
        
        # Determinar modo de ejecución
        env = os.environ.get('FLASK_ENV', 'development')
        
        if env == 'production':
            run_production()
        else:
            run_development()
            
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("Deteniendo servidor...")
        sys.exit(0)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()