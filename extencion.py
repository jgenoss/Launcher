from flask import current_app
from flask_socketio import SocketIO, emit  # Añade esta importación
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
socketio = SocketIO()