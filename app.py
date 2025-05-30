from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db
import os
import json
import hashlib
from datetime import datetime
import zipfile
from utils import format_file_size

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'updates'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'files'), exist_ok=True)
os.makedirs('static/downloads', exist_ok=True)

# Inicializar extensiones
db.init_app(app)

# IMPORTANTE: Inicializar SocketIO DESPUÉS de crear la app
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Importar modelos y rutas
from models import User, GameVersion, GameFile, UpdatePackage, NewsMessage

# Importar blueprints - DESPUÉS de crear socketio
from api_routes import api_bp
from admin_routes import admin_bp

# Registrar blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from markupsafe import Markup, escape

# Filtros de plantilla (mantén los existentes)
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    return Markup('<br>'.join(escape(s).splitlines()))

@app.template_filter('is_file_exists')
def is_file_exists_filter(path):
    return os.path.isfile(path)

@app.template_filter('get_total_size')
def get_total_size_filter(items):
    """Calcular tamaño total de una lista de elementos"""
    if not items:
        return 0
    total = 0
    for item in items:
        if hasattr(item, 'file_size') and item.file_size:
            total += item.file_size
    return total

@app.template_filter('get_file_size')
def get_file_size_filter(file_path):
    """Obtener tamaño de archivo formateado"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return format_file_size(size_bytes)
        return "0 B"
    except:
        return "0 B"

@app.template_filter('get_total_launcher_size')
def get_total_launcher_size_filter(launchers):
    """Calcular tamaño total de launchers"""
    total_bytes = 0
    for launcher in launchers:
        if launcher.file_path and os.path.exists(launcher.file_path):
            try:
                total_bytes += os.path.getsize(launcher.file_path)
            except:
                continue
    return format_file_size(total_bytes)

# ==================== RUTAS EXISTENTES ====================
@app.route('/')
def index():
    return redirect(url_for('admin.dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas para servir archivos estáticos del launcher
@app.route('/Launcher/<path:filename>')
def serve_launcher_files(filename):
    """Sirve archivos para el launcher C#"""
    return send_from_directory('static/downloads', filename)

@app.route('/Launcher/updates/<path:filename>')
def serve_update_files(filename):
    """Sirve archivos de actualización"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'updates'), filename)

@app.route('/Launcher/files/<path:filename>')
def serve_game_files(filename):
    """Sirve archivos individuales del juego"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'files'), filename)

# ===== EVENTOS DE SOCKETIO =====

@socketio.on('connect', namespace='/admin')
def handle_admin_connect():
    """Cuando un admin se conecta"""
    print(f'Admin conectado: {request.sid}')
    emit('connection_status', {
        'status': 'connected',
        'message': 'Conexión establecida con el panel de administración'
    })

@socketio.on('disconnect', namespace='/admin')
def handle_admin_disconnect():
    """Cuando un admin se desconecta"""
    print(f'Admin desconectado: {request.sid}')

@socketio.on('request_stats', namespace='/admin')
def handle_stats_request():
    """Cuando se solicitan estadísticas en tiempo real"""
    try:
        # Aquí puedes obtener estadísticas en tiempo real
        from models import DownloadLog, GameVersion
        
        total_downloads = DownloadLog.query.count()
        latest_version = GameVersion.get_latest()
        
        stats = {
            'total_downloads': total_downloads,
            'latest_version': latest_version.version if latest_version else 'N/A',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        emit('stats_update', stats)
    except Exception as e:
        emit('error', {'message': f'Error obteniendo estadísticas: {str(e)}'})

@socketio.on('ping', namespace='/admin')
def handle_ping():
    """Responder a ping para mantener conexión"""
    emit('pong', {'timestamp': datetime.utcnow().isoformat()})

# Función para emitir notificaciones globales
def emit_admin_notification(message, type='info', data=None):
    """Emitir notificación a todos los admins conectados"""
    socketio.emit('notification', {
        'type': type,
        'message': message,
        'data': data or {},
        'timestamp': datetime.utcnow().isoformat()
    }, namespace='/admin')

def create_admin_user():
    """Crear usuario administrador por defecto"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@localhost',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado: admin/admin123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #create_admin_user()
        port = 5000
        print(f"Iniciando servidor en puerto {port}")
        socketio.run(app,debug=True, host='0.0.0.0', port=port)