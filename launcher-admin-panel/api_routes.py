from flask import Blueprint, jsonify, request, send_from_directory, current_app
from models import GameVersion, GameFile, UpdatePackage, LauncherVersion, NewsMessage, DownloadLog, db
import os
import json

api_bp = Blueprint('api', __name__)

def log_download(file_requested, file_type, success=True):
    """Registrar descarga en logs"""
    try:
        log = DownloadLog(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            file_requested=file_requested,
            file_type=file_type,
            success=success
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging download: {e}")

@api_bp.route('/launcher_update.json')
def launcher_update():
    """Endpoint para verificar actualizaciones del launcher"""
    try:
        current_launcher = LauncherVersion.get_current()
        
        if not current_launcher:
            return jsonify({
                "version": "1.0.0.0",
                "file_name": "LC.exe"
            }), 404
        
        log_download('launcher_update.json', 'launcher_check')
        
        return jsonify({
            "version": current_launcher.version,
            "file_name": current_launcher.filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/update.json')
def update_info():
    """Endpoint principal para información de actualizaciones del juego"""
    try:
        latest_version = GameVersion.get_latest()
        
        if not latest_version:
            return jsonify({
                "latest_version": "1.0.0.0",
                "updates": [],
                "file_hashes": []
            }), 404

        # Obtener todos los paquetes de actualización ordenados por versión
        updates = UpdatePackage.query.join(GameVersion).order_by(GameVersion.version).all()
        update_filenames = [f"update_{pkg.version.version}.zip" for pkg in updates]

        # Obtener hashes de archivos de la versión más reciente
        files = GameFile.query.filter_by(version_id=latest_version.id).all()
        file_hashes = [file.to_dict() for file in files]

        log_download('update.json', 'update_check')

        response_data = {
            "latest_version": latest_version.version,
            "updates": update_filenames,
            "file_hashes": file_hashes
        }

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/message.json')
def messages():
    """Endpoint para mensajes y noticias"""
    try:
        active_messages = NewsMessage.query.filter_by(is_active=True).order_by(NewsMessage.priority.desc(), NewsMessage.created_at.desc()).all()
        
        messages_data = [msg.to_dict() for msg in active_messages]
        
        log_download('message.json', 'messages')
        
        return jsonify(messages_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/banner.html')
def banner():
    """Endpoint para el banner HTML del launcher"""
    try:
        log_download('banner.html', 'banner')
        return send_from_directory('static/downloads', 'banner.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/files/<filename>')
def download_game_file(filename):
    """Endpoint para descargar archivos individuales del juego"""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'files', filename)
        
        if not os.path.exists(file_path):
            log_download(filename, 'game_file', success=False)
            return jsonify({"error": "File not found"}), 404
        
        log_download(filename, 'game_file')
        return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], 'files'), filename)
    except Exception as e:
        log_download(filename, 'game_file', success=False)
        return jsonify({"error": str(e)}), 500

@api_bp.route('/updates/<filename>')
def download_update(filename):
    """Endpoint para descargar paquetes de actualización"""
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'updates', filename)
        
        if not os.path.exists(file_path):
            log_download(filename, 'update', success=False)
            return jsonify({"error": "Update file not found"}), 404
        
        log_download(filename, 'update')
        return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER'], 'updates'), filename)
    except Exception as e:
        log_download(filename, 'update', success=False)
        return jsonify({"error": str(e)}), 500

@api_bp.route('/LauncherUpdater.exe')
def download_launcher_updater():
    """Endpoint para descargar el actualizador del launcher"""
    try:
        file_path = os.path.join('static/downloads', 'LauncherUpdater.exe')
        
        if not os.path.exists(file_path):
            log_download('LauncherUpdater.exe', 'launcher_updater', success=False)
            return jsonify({"error": "Launcher updater not found"}), 404
        
        log_download('LauncherUpdater.exe', 'launcher_updater')
        return send_from_directory('static/downloads', 'LauncherUpdater.exe')
    except Exception as e:
        log_download('LauncherUpdater.exe', 'launcher_updater', success=False)
        return jsonify({"error": str(e)}), 500

@api_bp.route('/status')
def api_status():
    """Endpoint para verificar el estado de la API"""
    try:
        latest_version = GameVersion.get_latest()
        launcher_version = LauncherVersion.get_current()
        total_files = GameFile.query.count()
        total_updates = UpdatePackage.query.count()
        
        return jsonify({
            "status": "online",
            "latest_game_version": latest_version.version if latest_version else "N/A",
            "current_launcher_version": launcher_version.version if launcher_version else "N/A",
            "total_files": total_files,
            "total_updates": total_updates,
            "timestamp": db.func.now()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/stats')
def download_stats():
    """Endpoint para estadísticas de descarga"""
    try:
        # Estadísticas básicas
        total_downloads = DownloadLog.query.count()
        successful_downloads = DownloadLog.query.filter_by(success=True).count()
        failed_downloads = DownloadLog.query.filter_by(success=False).count()
        
        # Descargas por tipo
        stats_by_type = db.session.query(
            DownloadLog.file_type, 
            db.func.count(DownloadLog.id).label('count')
        ).group_by(DownloadLog.file_type).all()
        
        # Archivos más descargados
        popular_files = db.session.query(
            DownloadLog.file_requested,
            db.func.count(DownloadLog.id).label('count')
        ).group_by(DownloadLog.file_requested).order_by(db.func.count(DownloadLog.id).desc()).limit(10).all()
        
        return jsonify({
            "total_downloads": total_downloads,
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads,
            "success_rate": round((successful_downloads / total_downloads * 100), 2) if total_downloads > 0 else 0,
            "downloads_by_type": {stat[0]: stat[1] for stat in stats_by_type},
            "popular_files": [{"file": stat[0], "downloads": stat[1]} for stat in popular_files]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({"error": "Internal server error"}), 500