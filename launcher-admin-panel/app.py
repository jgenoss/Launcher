from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_from_directory
from models import db #from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import hashlib
from datetime import datetime
import zipfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///launcher_admin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Crear directorios necesarios
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'updates'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'files'), exist_ok=True)
os.makedirs('static/downloads', exist_ok=True)

#db = SQLAlchemy(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Importar modelos y rutas
from models import User, GameVersion, GameFile, UpdatePackage, NewsMessage
from api_routes import api_bp
from admin_routes import admin_bp

# Registrar blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/admin')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
from markupsafe import Markup, escape

@app.template_filter('nl2br')
def nl2br_filter(s):
    if s is None:
        return ''
    return Markup('<br>'.join(escape(s).splitlines()))

@app.template_filter('is_file_exists')
def is_file_exists_filter(path):
    return os.path.isfile(path)

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
        create_admin_user()
    app.run(debug=True, host='0.0.0.0', port=5000)