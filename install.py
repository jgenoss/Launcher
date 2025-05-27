#!/usr/bin/env python3
"""
Script de instalación para Launcher Admin Panel
Configura la base de datos, crea directorios necesarios y usuario administrador
"""

import os
import sys
import getpass
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        'uploads',
        'uploads/updates',
        'uploads/files',
        'static/downloads',
        'backups',
        'logs',
        'temp'
    ]
    
    print("Creando estructura de directorios...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✓ {directory}")

def create_config_file():
    """Crear archivo de configuración básico"""
    config_content = """# Configuración del Launcher Admin Panel
# Copia este archivo como .env y modifica los valores según tu entorno

# Configuración básica
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

# Base de datos
DATABASE_URL=sqlite:///launcher_admin.db

# Archivos
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=524288000

# URLs del launcher
LAUNCHER_URL_BASE=http://localhost:5000/Launcher

# Seguridad
SESSION_COOKIE_SECURE=False
FORCE_HTTPS=False

# Logs
LOG_LEVEL=INFO
LOG_FILE=logs/launcher_admin.log

# Backup
BACKUP_ENABLED=True
BACKUP_INTERVAL=3600
BACKUP_RETENTION_DAYS=30
"""
    
    with open('.env.example', 'w') as f:
        f.write(config_content)
    
    print("  ✓ Archivo .env.example creado")

def setup_database():
    """Configurar base de datos"""
    print("Configurando base de datos...")
    
    try:
        # Importar después de que se creen los directorios
        from app import app, db
        from models import User, GameVersion, ServerSettings
        
        with app.app_context():
            # Crear tablas
            db.create_all()
            print("  ✓ Tablas de base de datos creadas")
            
            # Verificar si ya existe un usuario admin
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("  ℹ Usuario administrador ya existe")
                return
            
            # Crear usuario administrador
            print("\nConfiguración del usuario administrador:")
            while True:
                username = input("Usuario administrador [admin]: ").strip() or 'admin'
                email = input("Email del administrador: ").strip()
                
                if email:
                    break
                print("El email es requerido.")
            
            while True:
                password = getpass.getpass("Contraseña: ")
                password_confirm = getpass.getpass("Confirmar contraseña: ")
                
                if password == password_confirm and len(password) >= 6:
                    break
                elif password != password_confirm:
                    print("Las contraseñas no coinciden.")
                else:
                    print("La contraseña debe tener al menos 6 caracteres.")
            
            # Crear usuario administrador
            admin = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=True
            )
            
            db.session.add(admin)
            
            # Crear configuraciones por defecto
            default_settings = [
                ('maintenance_mode', 'false', 'Modo de mantenimiento'),
                ('allow_registration', 'false', 'Permitir registro de usuarios'),
                ('max_file_size', '524288000', 'Tamaño máximo de archivo en bytes'),
                ('launcher_update_check_interval', '300', 'Intervalo de verificación de actualización del launcher (segundos)'),
                ('auto_backup_enabled', 'true', 'Backup automático habilitado'),
                ('log_retention_days', '30', 'Días de retención de logs'),
            ]
            
            for key, value, description in default_settings:
                setting = ServerSettings(
                    key=key,
                    value=value,
                    description=description
                )
                db.session.add(setting)
            
            db.session.commit()
            print(f"  ✓ Usuario administrador '{username}' creado")
            print("  ✓ Configuración por defecto establecida")
            
    except ImportError as e:
        print(f"  ✗ Error importando módulos: {e}")
        print("  Asegúrate de que todas las dependencias estén instaladas")
        return False
    except Exception as e:
        print(f"  ✗ Error configurando base de datos: {e}")
        return False
    
    return True

def create_sample_banner():
    """Crear banner HTML de ejemplo"""
    banner_content = """<!DOCTYPE html>
<html>
<head>
    <title>Game Launcher</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .banner-content {
            text-align: center;
            padding: 20px;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .title {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        .subtitle {
            font-size: 1rem;
            opacity: 0.8;
        }
        .news-item {
            background: rgba(255, 255, 255, 0.1);
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffd700;
        }
    </style>
</head>
<body>
    <div class="banner-content">
        <div class="logo">🎮</div>
        <div class="title">Mi Juego</div>
        <div class="subtitle">Panel de Administración Configurado</div>
        
        <div style="margin-top: 2rem;">
            <div class="news-item">
                <strong>🔥 ¡Servidor configurado!</strong><br>
                El panel de administración está listo para usar.
            </div>
            <div class="news-item">
                <strong>📝 Personaliza este banner</strong><br>
                Edita el archivo banner.html para personalizar esta vista.
            </div>
            <div class="news-item">
                <strong>🚀 ¡Comienza a gestionar!</strong><br>
                Sube archivos, crea versiones y gestiona actualizaciones.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    banner_path = 'static/downloads/banner.html'
    with open(banner_path, 'w', encoding='utf-8') as f:
        f.write(banner_content)
    
    print(f"  ✓ Banner de ejemplo creado en {banner_path}")

def create_gitignore():
    """Crear archivo .gitignore"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3

# Uploads and files
uploads/
static/downloads/*
!static/downloads/.gitkeep

# Logs
logs/
*.log

# Backups
backups/

# Temporary files
temp/
*.tmp

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Coverage
.coverage
htmlcov/

# Testing
.pytest_cache/
.tox/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("  ✓ Archivo .gitignore creado")

def create_readme():
    """Crear archivo README"""
    readme_content = """# Launcher Admin Panel

Panel de administración web para gestionar actualizaciones, archivos y versiones de tu juego.

## Características

- 🎮 Gestión completa de versiones del juego
- 📁 Subida y gestión de archivos
- 📦 Creación de paquetes de actualización
- 🚀 Gestión de versiones del launcher
- 📢 Sistema de mensajes y noticias
- 📊 Estadísticas de descarga en tiempo real
- 🔐 Sistema de autenticación seguro
- 📱 Interfaz responsive con Bootstrap

## Instalación

1. Clona el repositorio:
```bash
git clone <tu-repositorio>
cd launcher-admin-panel
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta el script de instalación:
```bash
python install.py
```

5. Copia y configura el archivo de entorno:
```bash
cp .env.example .env
# Edita .env con tu configuración
```

6. Inicia la aplicación:
```bash
python app.py
```

## Uso

1. Accede a `http://localhost:5000`
2. Inicia sesión con las credenciales del administrador
3. Comienza a gestionar tus versiones y archivos

### Creando tu primera versión

1. Ve a **Versiones del Juego** → **Nueva Versión**
2. Ingresa el número de versión (ej: 1.0.0.0)
3. Añade notas de la versión
4. Marca como "Versión actual" si es la primera

### Subiendo archivos

1. Ve a **Archivos del Juego** → **Subir Archivos**
2. Selecciona la versión
3. Arrastra o selecciona los archivos
4. Configura las rutas relativas
5. Haz clic en "Subir Archivos"

### Creando paquetes de actualización

1. Ve a **Paquetes de Actualización** → **Crear Actualización**
2. Selecciona la versión
3. Sube el archivo ZIP con los archivos de actualización
4. El sistema generará automáticamente el paquete

## API Endpoints

La aplicación expone varios endpoints para el launcher en C#:

- `GET /Launcher/launcher_update.json` - Información de actualización del launcher
- `GET /Launcher/update.json` - Información de actualizaciones del juego
- `GET /Launcher/message.json` - Mensajes y noticias
- `GET /Launcher/banner.html` - Banner HTML para el launcher
- `GET /Launcher/files/<filename>` - Descarga de archivos individuales
- `GET /Launcher/updates/<filename>` - Descarga de paquetes de actualización

## Configuración del Launcher C#

Para que tu launcher en C# funcione con este panel, asegúrate de que apunte a:

```csharp
private string Urls = "http://tu-servidor:5000/Launcher/";
```

## Estructura de Directorios

```
launcher-admin-panel/
├── app.py                 # Aplicación principal
├── models.py             # Modelos de base de datos
├── api_routes.py         # Rutas de la API
├── admin_routes.py       # Rutas del panel admin
├── utils.py              # Utilidades
├── config.py             # Configuración
├── requirements.txt      # Dependencias Python
├── uploads/              # Archivos subidos
│   ├── files/           # Archivos del juego
│   └── updates/         # Paquetes de actualización
├── static/downloads/     # Archivos estáticos públicos
├── templates/           # Plantillas HTML
└── logs/               # Archivos de log
```

## Desarrollo

Para contribuir al proyecto:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## Soporte

Si encuentras algún problema o tienes sugerencias, por favor crea un issue en el repositorio.
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  ✓ Archivo README.md creado")

def create_systemd_service():
    """Crear archivo de servicio systemd para producción"""
    service_content = """[Unit]
Description=Launcher Admin Panel
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/launcher-admin-panel
Environment=PATH=/path/to/launcher-admin-panel/venv/bin
ExecStart=/path/to/launcher-admin-panel/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('launcher-admin.service', 'w') as f:
        f.write(service_content)
    
    print("  ✓ Archivo de servicio systemd creado (launcher-admin.service)")

def main():
    """Función principal de instalación"""
    print("=== Launcher Admin Panel - Instalación ===\n")
    
    # Verificar Python
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 o superior es requerido")
        sys.exit(1)
    
    print("✅ Python version válida")
    
    # Crear directorios
    create_directories()
    
    # Crear archivos de configuración
    print("\nCreando archivos de configuración...")
    create_config_file()
    create_gitignore()
    create_readme()
    create_systemd_service()
    
    # Crear banner de ejemplo
    print("\nCreando contenido de ejemplo...")
    create_sample_banner()
    
    # Configurar base de datos
    print("\nConfigurando base de datos...")
    if not setup_database():
        print("❌ Error en la configuración de la base de datos")
        sys.exit(1)
    
    # Crear archivo .gitkeep para directorios vacíos
    gitkeep_dirs = ['static/downloads', 'uploads/files', 'uploads/updates', 'logs', 'backups']
    for directory in gitkeep_dirs:
        gitkeep_path = os.path.join(directory, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('')
    
    print("\n🎉 ¡Instalación completada exitosamente!")
    print("\nPróximos pasos:")
    print("1. Copia .env.example a .env y configura tus variables de entorno")
    print("2. Ejecuta 'python app.py' para iniciar el servidor")
    print("3. Accede a http://localhost:5000")
    print("4. Inicia sesión con las credenciales del administrador que configuraste")
    print("\n📖 Lee el archivo README.md para más información")

if __name__ == "__main__":
    main()