# 🎮 Launcher Admin Panel

[![Python](https://img.shields.io/badge/Python-3.7+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Panel de administración web completo para gestionar actualizaciones, archivos y versiones de tu launcher de juegos.**

![Dashboard Preview](docs/images/dashboard-preview.png)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Instalación Rápida](#-instalación-rápida)
- [Instalación Manual](#-instalación-manual)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Documentation](#-api-documentation)
- [Integración con Launcher C#](#-integración-con-launcher-c)
- [Docker](#-docker)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Soporte](#-soporte)

## ✨ Características

### 🚀 Gestión Completa
- **Versiones del Juego**: Crear, gestionar y activar diferentes versiones
- **Archivos del Juego**: Subida masiva con verificación MD5 automática
- **Paquetes de Actualización**: Creación de ZIPs con secuenciamiento automático
- **Launcher Management**: Gestión de versiones del propio launcher

### 📊 Monitoreo y Estadísticas
- **Dashboard en Tiempo Real**: Estadísticas de uso y descargas
- **Logs Detallados**: Seguimiento completo de todas las descargas
- **Gráficos Interactivos**: Visualización de datos con Chart.js
- **Alertas Automáticas**: Notificaciones de errores y eventos importantes

### 🔐 Seguridad y Control
- **Autenticación Segura**: Sistema de login con sesiones encriptadas
- **Control de Acceso**: Diferentes niveles de permisos de usuario
- **Rate Limiting**: Protección contra abuso de API
- **Validación de Archivos**: Verificación de integridad con MD5

### 🎨 Interfaz Moderna
- **Responsive Design**: Compatible con desktop, tablet y móvil
- **Bootstrap 5**: Interfaz moderna y profesional
- **Tema Oscuro/Claro**: Soporte para múltiples temas
- **Animaciones Suaves**: Experiencia de usuario fluida

### 🔧 API Completa
- **RESTful API**: Endpoints para todas las funcionalidades
- **Documentación OpenAPI**: Swagger UI integrado
- **Webhooks**: Integración con Discord, Slack y otros servicios
- **Versionado**: API versionada para compatibilidad

### 📱 Sistema de Mensajes
- **Noticias del Juego**: Sistema de mensajes para el launcher
- **Prioridades**: Gestión de importancia de mensajes
- **Tipos Personalizados**: Actualizaciones, eventos, mantenimiento, etc.
- **Vista Previa**: Simulación en tiempo real del launcher

## 📸 Capturas de Pantalla

### Dashboard Principal
![Dashboard](docs/images/dashboard.png)

### Gestión de Versiones
![Versions](docs/images/versions.png)

### Subida de Archivos
![Upload](docs/images/upload.png)

### Logs de Descarga
![Logs](docs/images/logs.png)

## 🚀 Instalación Rápida

### Usando el Script Automático (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/launcher-admin-panel.git
cd launcher-admin-panel

# Ejecutar script de instalación
chmod +x setup.sh
./setup.sh

# Iniciar el servidor
source venv/bin/activate
python run.py
```

### Usando Docker (Más Rápido)

```bash
# Clonar y ejecutar con Docker Compose
git clone https://github.com/tu-usuario/launcher-admin-panel.git
cd launcher-admin-panel

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f launcher-admin
```

## 🔧 Instalación Manual

### Prerrequisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos Detallados

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/launcher-admin-panel.git
   cd launcher-admin-panel
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En Linux/macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurar entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tu configuración
   ```

5. **Inicializar base de datos**
   ```bash
   python install.py
   ```

6. **Iniciar la aplicación**
   ```bash
   python run.py
   ```

7. **Acceder al panel**
   - URL: http://localhost:5000
   - Usuario: `admin`
   - Contraseña: `admin123`

## ⚙️ Configuración

### Variables de Entorno Principales

```bash
# Configuración básica
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-muy-segura
PORT=5000

# Base de datos
DATABASE_URL=sqlite:///launcher_admin.db
# Para PostgreSQL: postgresql://user:pass@host:port/db

# Archivos
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=524288000  # 500MB

# URLs del launcher
LAUNCHER_URL_BASE=http://tu-dominio.com/Launcher

# Seguridad
FORCE_HTTPS=false
ENABLE_RATE_LIMIT=true
API_RATE_LIMIT=100

# Notificaciones
NOTIFICATION_ENABLED=false
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Configuración de Base de Datos

#### SQLite (Desarrollo)
```bash
DATABASE_URL=sqlite:///launcher_admin.db
```

#### PostgreSQL (Producción Recomendada)
```bash
DATABASE_URL=postgresql://usuario:contraseña@host:5432/launcher_db
```

#### MySQL
```bash
DATABASE_URL=mysql://usuario:contraseña@host:3306/launcher_db
```

### Configuración de Nginx (Producción)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /Launcher/ {
        alias /path/to/launcher-admin-panel/uploads/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📖 Uso

### 1. Gestión de Versiones

1. **Crear Nueva Versión**
   - Ve a `Versiones del Juego` → `Nueva Versión`
   - Ingresa número de versión (ej: 1.0.0.0)
   - Añade notas de la versión
   - Marca como "Versión actual" si es necesario

2. **Subir Archivos**
   - Ve a `Archivos del Juego` → `Subir Archivos`
   - Selecciona la versión
   - Arrastra archivos o usa el selector
   - Configura rutas relativas
   - Los hashes MD5 se calculan automáticamente

3. **Crear Paquete de Actualización**
   - Ve a `Paquetes de Actualización` → `Crear Actualización`
   - Selecciona la versión
   - Sube un archivo ZIP con los archivos modificados
   - El sistema genera automáticamente `update_X.X.X.X.zip`

### 2. Gestión del Launcher

1. **Subir Nueva Versión del Launcher**
   - Ve a `Versiones del Launcher` → `Subir Nueva Versión`
   - Sube el archivo .exe del launcher
   - Configura como versión actual
   - El sistema actualiza automáticamente `launcher_update.json`

### 3. Sistema de Mensajes

1. **Crear Mensajes para el Launcher**
   - Ve a `Mensajes y Noticias` → `Nuevo Mensaje`
   - Selecciona tipo (Actualización, Noticia, Evento, etc.)
   - Escribe el mensaje (máx. 500 caracteres)
   - Configura prioridad (1-5)
   - Activa/desactiva según necesidad

### 4. Monitoreo

1. **Dashboard**: Vista general con estadísticas en tiempo real
2. **Logs de Descarga**: Seguimiento detallado de todas las descargas
3. **Configuración**: Ajustes del sistema y notificaciones

## 🔌 API Documentation

### Endpoints Principales

#### Información del Launcher
```http
GET /api/launcher_update.json
```
Respuesta:
```json
{
  "version": "1.0.0.2",
  "file_name": "LC.exe"
}
```

#### Información de Actualizaciones del Juego
```http
GET /api/update.json
```
Respuesta:
```json
{
  "latest_version": "1.0.0.3",
  "updates": [
    "update_1.0.0.0.zip",
    "update_1.0.0.1.zip",
    "update_1.0.0.2.zip",
    "update_1.0.0.3.zip"
  ],
  "file_hashes": [
    {
      "FileName": "Nksp.exe",
      "MD5Hash": "d41d8cd98f00b204e9800998ecf8427e",
      "RelativePath": "bin/Nksp.exe"
    }
  ]
}
```

#### Mensajes del Launcher
```http
GET /api/message.json
```
Respuesta:
```json
[
  {
    "type": "Actualización",
    "message": "Nueva funcionalidad agregada."
  },
  {
    "type": "Noticia",
    "message": "¡Evento especial este fin de semana!"
  }
]
```

#### Estado de la API
```http
GET /api/status
```

#### Estadísticas
```http
GET /api/stats
```

### Descargas de Archivos

```http
# Descargar paquete de actualización
GET /Launcher/updates/update_1.0.0.3.zip

# Descargar archivo del juego
GET /Launcher/files/Nksp.exe

# Descargar launcher
GET /Launcher/LC.exe

# Banner HTML
GET /Launcher/banner.html
```

## 🎯 Integración con Launcher C#

### Configuración en el Launcher

```csharp
private string Urls = "http://tu-dominio.com/Launcher/";
private string UrbBanner = "http://tu-dominio.com/Launcher/banner.html";
```

### Verificación de Actualizaciones

El launcher C# debe consultar estos endpoints:

1. **Actualización del Launcher**: `/api/launcher_update.json`
2. **Actualizaciones del Juego**: `/api/update.json`
3. **Mensajes**: `/api/message.json`
4. **Banner**: `/Launcher/banner.html`

### Flujo de Actualización

1. Launcher consulta `/api/update.json`
2. Compara versión local con `latest_version`
3. Si hay actualización, descarga los ZIPs necesarios desde `/Launcher/updates/`
4. Verifica integridad con MD5 de `file_hashes`
5. Extrae archivos y actualiza el juego

## 🐳 Docker

### Docker Compose (Recomendado)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Solo la aplicación
docker-compose up launcher-admin

# Con base de datos PostgreSQL
docker-compose --profile with-postgres up -d

# Con Nginx
docker-compose --profile with-nginx up -d

# Backup de base de datos
docker-compose --profile backup run backup

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Docker Manual

```bash
# Construir imagen
docker build -t launcher-admin-panel .

# Ejecutar contenedor
docker run -d \
  --name launcher-admin \
  -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY=tu-clave-secreta \
  launcher-admin-panel
```

### Variables de Entorno Docker

```yaml
environment:
  - FLASK_ENV=production
  - SECRET_KEY=clave-super-secreta
  - DATABASE_URL=postgresql://user:pass@db:5432/launcher_db
  - WORKERS=4
```

## 🔄 Backup y Restauración

### Backup Automático

```bash
# Configurar en .env
BACKUP_ENABLED=true
BACKUP_INTERVAL=3600  # 1 hora
BACKUP_RETENTION_DAYS=30
```

### Backup Manual

```bash
# Base de datos SQLite
cp launcher_admin.db backups/backup_$(date +%Y%m%d_%H%M%S).db

# Base de datos PostgreSQL
pg_dump launcher_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Archivos
tar -czf backups/files_$(date +%Y%m%d_%H%M%S).tar.gz uploads/
```

### Restauración

```bash
# SQLite
cp backups/backup_YYYYMMDD_HHMMSS.db launcher_admin.db

# PostgreSQL
psql launcher_db < backups/backup_YYYYMMDD_HHMMSS.sql
```

## 🛠️ Desarrollo

### Configuración de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
python -m pytest

# Ejecutar con auto-reload
FLASK_ENV=development python run.py

# Formatear código
black .
isort .

# Linting
flake8 .
pylint app/
```

### Estructura del Proyecto

```
launcher-admin-panel/
├── app.py                 # Aplicación principal Flask
├── models.py              # Modelos de base de datos
├── api_routes.py          # Rutas de la API
├── admin_routes.py        # Rutas del panel admin
├── utils.py               # Utilidades y helpers
├── config.py              # Configuración
├── run.py                 # Script de inicio
├── install.py             # Script de instalación
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación Docker
├── setup.sh              # Script de instalación automática
├── .env.example          # Ejemplo de configuración
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   └── admin/
│       ├── dashboard.html
│       ├── versions.html
│       ├── files.html
│       ├── uploads.html
│       ├── messages.html
│       └── ...
├── static/               # Archivos estáticos
│   └── downloads/
│       └── banner.html
├── uploads/              # Archivos subidos
│   ├── files/
│   └── updates/
├── logs/                 # Archivos de log
├── backups/              # Backups automáticos
└── docs/                 # Documentación
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest

# Tests específicos
python -m pytest tests/test_api.py

# Con cobertura
python -m pytest --cov=app

# Tests de integración
python -m pytest tests/integration/
```

### Tests Incluidos

- **Tests de API**: Verificación de todos los endpoints
- **Tests de Modelos**: Validación de base de datos
- **Tests de Upload**: Subida de archivos
- **Tests de Seguridad**: Autenticación y autorización
- **Tests de Integración**: Flujo completo de actualización

## 📚 Documentación Adicional

- [Guía de Instalación Detallada](docs/installation.md)
- [Configuración Avanzada](docs/configuration.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing Guidelines](docs/contributing.md)
- [Changelog](CHANGELOG.md)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Reportar Bugs

Si encuentras un bug, por favor [abre un issue](https://github.com/tu-usuario/launcher-admin-panel/issues) con:

- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots si es aplicable
- Información del entorno (OS, Python version, etc.)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 💬 Soporte

- **Documentation**: [Wiki del proyecto](https://github.com/tu-usuario/launcher-admin-panel/wiki)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/launcher-admin-panel/issues)
- **Discord**: [Canal de soporte](https://discord.gg/tu-canal)
- **Email**: admin@tu-dominio.com

## 🙏 Agradecimientos

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [Chart.js](https://www.chartjs.org/) - Gráficos interactivos
- [SQLAlchemy](https://sqlalchemy.org/) - ORM para Python

---

<div align="center">

**[⬆ Volver arriba](#-launcher-admin-panel)**

Made with ❤️ for the gaming community

</div>