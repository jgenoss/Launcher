# Launcher Admin Panel

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
source venv/bin/activate  # En Windows: venv\Scripts\activate
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

- `GET /Launcher/launcher_update` - Información de actualización del launcher
- `GET /Launcher/update` - Información de actualizaciones del juego
- `GET /Launcher/message` - Mensajes y noticias
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
