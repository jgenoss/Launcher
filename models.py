from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }


class GameVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), unique=True, nullable=False)
    is_latest = db.Column(db.Boolean, default=False)
    release_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relaciones
    update_packages = db.relationship('UpdatePackage', backref='version', lazy=True)
    files = db.relationship('GameFile', backref='version', lazy=True)

    def __repr__(self):
        return f'<GameVersion {self.version}>'

    @staticmethod
    def get_latest():
        return GameVersion.query.filter_by(is_latest=True).first()

    def set_as_latest(self):
        # Desmarcar la versión actual como latest
        current_latest = GameVersion.get_latest()
        if current_latest:
            current_latest.is_latest = False
        
        # Marcar esta versión como latest
        self.is_latest = True
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'is_latest': self.is_latest,
            'release_notes': self.release_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by,
            'files': [f.to_dict() for f in self.files],
            'update_packages': [u.id for u in self.update_packages]
        }

class UpdatePackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('game_version.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    md5_hash = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<UpdatePackage {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'version_id': self.version_id,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'md5_hash': self.md5_hash,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': self.uploaded_by
        }


class GameFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    relative_path = db.Column(db.String(500), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)
    file_size = db.Column(db.Integer)
    version_id = db.Column(db.Integer, db.ForeignKey('game_version.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GameFile {self.filename}>'

    def to_dict(self):
        return {
            'FileName': self.filename,
            'RelativePath': self.relative_path,
            'MD5Hash': self.md5_hash
        }

class LauncherVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    release_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<LauncherVersion {self.version}>'

    @staticmethod
    def get_current():
        return LauncherVersion.query.filter_by(is_current=True).first()

    def set_as_current(self):
        # Desmarcar la versión actual
        current = LauncherVersion.get_current()
        if current:
            current.is_current = False
        
        # Marcar esta versión como actual
        self.is_current = True
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'version': self.version,
            'filename': self.filename,
            'file_path': self.file_path,
            'is_current': self.is_current,
            'release_notes': self.release_notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }


class NewsMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'Actualización', 'Noticia', etc.
    message = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # Para ordenamiento
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<NewsMessage {self.type}: {self.message[:50]}>'

    def to_dict(self):
        return {
            'type': self.type,
            'message': self.message
        }

class ServerSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<ServerSettings {self.key}: {self.value}>'

    @staticmethod
    def get_value(key, default=None):
        setting = ServerSettings.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set_value(key, value, description=None):
        setting = ServerSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = ServerSettings(key=key, value=value, description=description)
            db.session.add(setting)
        
        db.session.commit()
        return setting

class DownloadLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500))
    file_requested = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # 'update', 'launcher', 'game_file'
    success = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DownloadLog {self.ip_address}: {self.file_requested}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'file_requested': self.file_requested,
            'file_type': self.file_type,
            'success': self.success,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
