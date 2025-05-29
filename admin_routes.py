from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import (GameVersion, GameFile, UpdatePackage, LauncherVersion, 
                   NewsMessage, DownloadLog, ServerSettings, User, db)
import os
import hashlib
import zipfile
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def calculate_md5(file_path):
    """Calcular MD5 de un archivo"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@admin_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        # Estadísticas generales
        total_versions = GameVersion.query.count()
        total_files = GameFile.query.count()
        total_updates = UpdatePackage.query.count()
        total_downloads = DownloadLog.query.count()
        
        # Versión actual
        latest_version = GameVersion.get_latest()
        current_launcher = LauncherVersion.get_current()
        print("Última versión:", latest_version)
        # Descargas recientes (últimas 24 horas)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_downloads = DownloadLog.query.filter(DownloadLog.created_at >= yesterday).count()
        
        # Mensajes activos
        active_messages = NewsMessage.query.filter_by(is_active=True).count()
        
        # Gráfico de descargas por día (últimos 7 días)
        downloads_by_day = []
        for i in range(7):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = DownloadLog.query.filter(
                DownloadLog.created_at >= day_start,
                DownloadLog.created_at < day_end
            ).count()
            
            downloads_by_day.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        
        downloads_by_day.reverse()
        
        return render_template('admin/dashboard.html',
                             total_versions=total_versions,
                             total_files=total_files,
                             total_updates=total_updates,
                             total_downloads=total_downloads,
                             latest_version=latest_version,
                             current_launcher=current_launcher,
                             recent_downloads=recent_downloads,
                             active_messages=active_messages,
                             downloads_by_day=downloads_by_day)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html')

@admin_bp.route('/versions')
@login_required
def versions():
    """Gestión de versiones del juego"""
    versions = GameVersion.query.order_by(GameVersion.created_at.desc()).all()
    return render_template('admin/versions.html', versions=versions)

@admin_bp.route('/versions/create', methods=['GET', 'POST'])
@login_required
def create_version():
    """Crear nueva versión"""
    if request.method == 'POST':
        try:
            version = request.form['version']
            release_notes = request.form['release_notes']
            is_latest = 'is_latest' in request.form
            
            # Verificar que la versión no exista
            existing = GameVersion.query.filter_by(version=version).first()
            if existing:
                flash('Esta versión ya existe', 'error')
                return render_template('admin/create_version.html')
            
            new_version = GameVersion(
                version=version,
                release_notes=release_notes,
                created_by=current_user.id
            )
            
            db.session.add(new_version)
            db.session.commit()
            
            if is_latest:
                new_version.set_as_latest()
            
            flash(f'Versión {version} creada exitosamente', 'success')
            return redirect(url_for('admin.versions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear versión: {str(e)}', 'error')
    
    return render_template('admin/create_version.html')

@admin_bp.route('/versions/<int:version_id>/set_latest')
@login_required
def set_latest_version(version_id):
    """Establecer versión como la más reciente"""
    try:
        version = GameVersion.query.get_or_404(version_id)
        version.set_as_latest()
        flash(f'Versión {version.version} establecida como la más reciente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.versions'))

@admin_bp.route('/files')
@login_required
def files():
    """Gestión de archivos del juego"""
    page = request.args.get('page', 1, type=int)
    version_id = request.args.get('version_id', None, type=int)
    
    query = GameFile.query
    if version_id:
        query = query.filter_by(version_id=version_id)
    
    files = query.order_by(GameFile.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    versions = GameVersion.query.order_by(GameVersion.version.desc()).all()
    
    return render_template('admin/files.html', files=files, versions=versions, current_version_id=version_id)

@admin_bp.route('/files/upload', methods=['GET', 'POST'])
@login_required
def upload_files():
    """Subir archivos del juego"""
    if request.method == 'POST':
        try:
            version_id = request.form['version_id']
            uploaded_files = request.files.getlist('files')
            
            version = GameVersion.query.get_or_404(version_id)
            files_uploaded = 0
            
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    relative_path = request.form.get(f'relative_path_{file.filename}', f'bin/{filename}')
                    
                    # Guardar archivo
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'files', filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
                    
                    # Calcular MD5
                    md5_hash = calculate_md5(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    # Verificar si el archivo ya existe
                    existing_file = GameFile.query.filter_by(
                        filename=filename, 
                        version_id=version_id
                    ).first()
                    
                    if existing_file:
                        # Actualizar archivo existente
                        existing_file.md5_hash = md5_hash
                        existing_file.file_size = file_size
                        existing_file.relative_path = relative_path
                        existing_file.updated_at = datetime.utcnow()
                    else:
                        # Crear nuevo registro
                        game_file = GameFile(
                            filename=filename,
                            relative_path=relative_path,
                            md5_hash=md5_hash,
                            file_size=file_size,
                            version_id=version_id
                        )
                        db.session.add(game_file)
                    
                    files_uploaded += 1
            
            db.session.commit()
            flash(f'{files_uploaded} archivos subidos exitosamente', 'success')
            return redirect(url_for('admin.files'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al subir archivos: {str(e)}', 'error')
    
    versions = GameVersion.query.order_by(GameVersion.version.desc()).all()
    versions_data = [v.to_dict() for v in versions]
    return render_template('admin/upload_files.html', versions=versions, versions_data=versions_data)


@admin_bp.route('/updates')
@login_required
def updates():
    """Gestión de paquetes de actualización"""
    updates = UpdatePackage.query.join(GameVersion).order_by(GameVersion.version.desc()).all()
    return render_template('admin/updates.html', updates=updates)

@admin_bp.route('/updates/create', methods=['GET', 'POST'])
@login_required
def create_update():
    """Crear paquete de actualización"""
    if request.method == 'POST':
        try:
            version_id = request.form['version_id']
            update_file = request.files['update_file']
            
            if not update_file or not update_file.filename:
                flash('Debe seleccionar un archivo', 'error')
                return render_template('admin/create_update.html')
            
            if not update_file.filename.lower().endswith('.zip'):
                flash('Solo se permiten archivos ZIP', 'error')
                return render_template('admin/create_update.html', versions=GameVersion.query.order_by(GameVersion.version.desc()).all())
            
            version = GameVersion.query.get_or_404(version_id)
            filename = f"update_{version.version}.zip"
            
            # Guardar archivo
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'updates', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            update_file.save(file_path)
            
            # Calcular MD5 y tamaño
            md5_hash = calculate_md5(file_path)
            file_size = os.path.getsize(file_path)
            
            # Verificar si ya existe un paquete para esta versión
            existing_update = UpdatePackage.query.filter_by(version_id=version_id).first()
            if existing_update:
                # Eliminar archivo anterior
                old_path = existing_update.file_path
                if os.path.exists(old_path):
                    os.remove(old_path)
                
                # Actualizar registro
                existing_update.filename = filename
                existing_update.file_path = file_path
                existing_update.file_size = file_size
                existing_update.md5_hash = md5_hash
            else:
                # Crear nuevo registro
                update_package = UpdatePackage(
                    filename=filename,
                    version_id=version_id,
                    file_path=file_path,
                    file_size=file_size,
                    md5_hash=md5_hash,
                    uploaded_by=current_user.id
                )
                db.session.add(update_package)
            
            db.session.commit()
            flash(f'Paquete de actualización creado para versión {version.version}', 'success')
            return redirect(url_for('admin.updates'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear paquete: {str(e)}', 'error')
    
    versions = GameVersion.query.order_by(GameVersion.version.desc()).all()
    return render_template('admin/create_update.html', versions=versions)

@admin_bp.route('/launcher')
@login_required
def launcher_versions():
    """Gestión de versiones del launcher"""
    launchers = LauncherVersion.query.order_by(LauncherVersion.created_at.desc()).all()
    return render_template('admin/launcher.html', launchers=launchers)

@admin_bp.route('/launcher/upload', methods=['GET', 'POST'])
@login_required
def upload_launcher():
    """Subir nueva versión del launcher"""
    if request.method == 'POST':
        try:
            version = request.form['version']
            launcher_file = request.files['launcher_file']
            release_notes = request.form['release_notes']
            is_current = 'is_current' in request.form
            
            if not launcher_file or not launcher_file.filename:
                flash('Debe seleccionar un archivo', 'error')
                return render_template('admin/upload_launcher.html')
            
            if not allowed_file(launcher_file.filename, {'exe'}):
                flash('Solo se permiten archivos EXE', 'error')
                return render_template('admin/upload_launcher.html')
            
            filename = secure_filename(launcher_file.filename)
            file_path = os.path.join('static/downloads', filename)
            
            # Guardar archivo
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            launcher_file.save(file_path)
            
            # Crear registro
            launcher_version = LauncherVersion(
                version=version,
                filename=filename,
                file_path=file_path,
                release_notes=release_notes,
                created_by=current_user.id
            )
            
            db.session.add(launcher_version)
            db.session.commit()
            
            if is_current:
                launcher_version.set_as_current()
            
            flash(f'Launcher versión {version} subido exitosamente', 'success')
            return redirect(url_for('admin.launcher_versions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al subir launcher: {str(e)}', 'error')
    
    return render_template('admin/upload_launcher.html')

@admin_bp.route('/launcher/<int:launcher_id>/set_current')
@login_required
def set_current_launcher(launcher_id):
    """Establecer launcher como actual"""
    try:
        launcher = LauncherVersion.query.get_or_404(launcher_id)
        launcher.set_as_current()
        flash(f'Launcher versión {launcher.version} establecido como actual', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.launcher_versions'))

@admin_bp.route('/messages')
@login_required
def messages():
    """Gestión de mensajes y noticias"""
    messages = NewsMessage.query.order_by(NewsMessage.priority.desc(), NewsMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)

@admin_bp.route('/messages/create', methods=['GET', 'POST'])
@login_required
def create_message():
    """Crear mensaje/noticia"""
    if request.method == 'POST':
        try:
            message_type = request.form['type']
            message = request.form['message']
            priority = int(request.form['priority'])
            is_active = 'is_active' in request.form
            
            news_message = NewsMessage(
                type=message_type,
                message=message,
                priority=priority,
                is_active=is_active,
                created_by=current_user.id
            )
            
            db.session.add(news_message)
            db.session.commit()
            
            flash('Mensaje creado exitosamente', 'success')
            return redirect(url_for('admin.messages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear mensaje: {str(e)}', 'error')
    
    return render_template('admin/create_message.html')

@admin_bp.route('/messages/<int:message_id>/toggle')
@login_required
def toggle_message(message_id):
    """Activar/desactivar mensaje"""
    try:
        message = NewsMessage.query.get_or_404(message_id)
        message.is_active = not message.is_active
        db.session.commit()
        
        status = "activado" if message.is_active else "desactivado"
        flash(f'Mensaje {status} exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.messages'))

@admin_bp.route('/logs')
@login_required
def download_logs():
    """Ver logs de descarga con estadísticas corregidas"""
    page = request.args.get('page', 1, type=int)
    file_type = request.args.get('file_type', '')
    
    query = DownloadLog.query
    if file_type:
        query = query.filter_by(file_type=file_type)
    
    logs = query.order_by(DownloadLog.created_at.desc()).paginate(
        page=page, per_page=100, error_out=False
    )
    
    # ESTADÍSTICAS CORREGIDAS
    try:
        # Total de logs
        total_logs = DownloadLog.query.count()
        
        # Logs exitosos y fallidos
        successful_logs = DownloadLog.query.filter_by(success=True).count()
        failed_logs = DownloadLog.query.filter_by(success=False).count()
        
        # IPs únicas - CORREGIR PROBLEMA DE CONTEO
        unique_ips_query = db.session.query(DownloadLog.ip_address).distinct()
        unique_ips_count = unique_ips_query.count()
        
        # Tipos de archivo únicos para el filtro
        file_types_query = db.session.query(DownloadLog.file_type).distinct().filter(
            DownloadLog.file_type.isnot(None)
        ).all()
        file_types = [ft[0] for ft in file_types_query if ft[0]]
        
        # Estadísticas adicionales para la página
        stats = {
            'total_logs': total_logs,
            'successful_logs': successful_logs,
            'failed_logs': failed_logs,
            'unique_ips': unique_ips_count,
            'success_rate': round((successful_logs / total_logs * 100), 2) if total_logs > 0 else 0
        }
        
        current_app.logger.info(f"Estadísticas de logs calculadas: {stats}")
        
    except Exception as e:
        current_app.logger.error(f"Error calculando estadísticas de logs: {e}")
        stats = {
            'total_logs': 0,
            'successful_logs': 0,
            'failed_logs': 0,
            'unique_ips': 0,
            'success_rate': 0
        }
        file_types = []
    
    return render_template('admin/logs.html', logs=logs, file_types=file_types, current_file_type=file_type, stats=stats)

# 2. NUEVA RUTA PARA LIMPIAR LOGS ANTIGUOS
@admin_bp.route('/logs/cleanup', methods=['POST'])
@login_required
def cleanup_old_logs():
    """Limpiar logs antiguos"""
    try:
        # Obtener parámetros
        days = request.form.get('days', 30, type=int)
        confirm = request.form.get('confirm', 'false')
        
        if confirm != 'true':
            flash('Debes confirmar la acción para eliminar logs antiguos', 'error')
            return redirect(url_for('admin.download_logs'))
        
        # Calcular fecha límite
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Contar logs que se van a eliminar
        logs_to_delete = DownloadLog.query.filter(
            DownloadLog.created_at < cutoff_date
        ).count()
        
        if logs_to_delete == 0:
            flash(f'No hay logs anteriores a {days} días para eliminar', 'info')
            return redirect(url_for('admin.download_logs'))
        
        # Eliminar logs antiguos
        deleted_count = DownloadLog.query.filter(
            DownloadLog.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        current_app.logger.info(f"Eliminados {deleted_count} logs antiguos por usuario {current_user.username}")
        flash(f'{deleted_count} logs antiguos eliminados exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error limpiando logs antiguos: {e}")
        flash(f'Error al limpiar logs: {str(e)}', 'error')
    
    return redirect(url_for('admin.download_logs'))

@admin_bp.route('/logs/export')
@login_required
def export_logs():
    """Exportar logs como CSV"""
    try:
        from datetime import datetime
        import csv
        from io import StringIO
        
        # Obtener parámetros de filtro
        file_type = request.args.get('file_type', '')
        days = request.args.get('days', 30, type=int)
        
        # Crear query
        query = DownloadLog.query
        
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        if days > 0:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(DownloadLog.created_at >= cutoff_date)
        
        # Obtener logs
        logs = query.order_by(DownloadLog.created_at.desc()).all()
        
        # Crear CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Fecha', 'Hora', 'IP', 'Archivo', 'Tipo', 'Estado', 'User Agent'
        ])
        
        # Datos
        for log in logs:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d'),
                log.created_at.strftime('%H:%M:%S'),
                log.ip_address,
                log.file_requested,
                log.file_type or 'N/A',
                'Exitoso' if log.success else 'Fallido',
                log.user_agent or 'N/A'
            ])
        
        # Preparar respuesta
        from flask import make_response
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=logs_export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        
        current_app.logger.info(f"Logs exportados por usuario {current_user.username}")
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exportando logs: {e}")
        flash(f'Error al exportar logs: {str(e)}', 'error')
        return redirect(url_for('admin.download_logs'))

@admin_bp.route('/settings')
@login_required
def settings():
    """Configuración del servidor"""
    settings = ServerSettings.query.all()
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/versions/<int:version_id>/delete', methods=['POST'])
@login_required
def delete_version(version_id):
    """Eliminar versión"""
    try:
        version = GameVersion.query.get_or_404(version_id)
        
        # Verificar que no sea la versión actual
        if version.is_latest:
            flash('No se puede eliminar la versión actual', 'error')
            return redirect(url_for('admin.versions'))
        
        # Eliminar archivos asociados
        for game_file in version.files:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'files', game_file.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(game_file)
        
        # Eliminar paquetes de actualización asociados
        for update_package in version.update_packages:
            if os.path.exists(update_package.file_path):
                os.remove(update_package.file_path)
            db.session.delete(update_package)
        
        # Eliminar la versión
        db.session.delete(version)
        db.session.commit()
        
        flash(f'Versión {version.version} eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar versión: {str(e)}', 'error')
    
    return redirect(url_for('admin.versions'))

@admin_bp.route('/files/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(file_id):
    """Eliminar archivo individual"""
    try:
        game_file = GameFile.query.get_or_404(file_id)
        filename = game_file.filename
        
        # Eliminar archivo físico
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'files', game_file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            current_app.logger.info(f'Archivo físico eliminado: {file_path}')
        else:
            current_app.logger.warning(f'Archivo físico no encontrado: {file_path}')
        
        # Eliminar registro de la base de datos
        db.session.delete(game_file)
        db.session.commit()
        
        current_app.logger.info(f'Archivo {filename} eliminado exitosamente por usuario {current_user.username}')
        flash(f'Archivo {filename} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al eliminar archivo {file_id}: {str(e)}')
        flash(f'Error al eliminar archivo: {str(e)}', 'error')
    
    return redirect(url_for('admin.files'))

@admin_bp.route('/files/delete_selected', methods=['POST'])
@login_required
def delete_selected_files():
    """Eliminar archivos seleccionados"""
    try:
        file_ids = request.form.getlist('file_ids')
        if not file_ids:
            flash('No se seleccionaron archivos para eliminar', 'warning')
            return redirect(url_for('admin.files'))
        
        deleted_count = 0
        errors = []
        
        for file_id in file_ids:
            try:
                game_file = GameFile.query.get(file_id)
                if game_file:
                    filename = game_file.filename
                    
                    # Eliminar archivo físico
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'files', game_file.filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        current_app.logger.info(f'Archivo físico eliminado: {file_path}')
                    else:
                        current_app.logger.warning(f'Archivo físico no encontrado: {file_path}')
                    
                    # Eliminar registro de la base de datos
                    db.session.delete(game_file)
                    deleted_count += 1
                    current_app.logger.info(f'Archivo {filename} eliminado exitosamente')
                else:
                    errors.append(f'Archivo con ID {file_id} no encontrado')
            except Exception as e:
                errors.append(f'Error eliminando archivo ID {file_id}: {str(e)}')
                current_app.logger.error(f'Error eliminando archivo ID {file_id}: {str(e)}')
        
        db.session.commit()
        
        if deleted_count > 0:
            flash(f'{deleted_count} archivo(s) eliminado(s) exitosamente', 'success')
        
        if errors:
            for error in errors:
                flash(error, 'error')
                
        current_app.logger.info(f'{deleted_count} archivos eliminados por usuario {current_user.username}')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error general al eliminar archivos: {str(e)}')
        flash(f'Error al eliminar archivos: {str(e)}', 'error')
    
    return redirect(url_for('admin.files'))

@admin_bp.route('/updates/<int:update_id>/delete', methods=['POST'])
@login_required
def delete_update(update_id):
    """Eliminar paquete de actualización"""
    try:
        update_package = UpdatePackage.query.get_or_404(update_id)
        
        # Eliminar archivo físico
        if os.path.exists(update_package.file_path):
            os.remove(update_package.file_path)
        
        # Eliminar registro de la base de datos
        db.session.delete(update_package)
        db.session.commit()
        
        flash(f'Paquete de actualización {update_package.filename} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar paquete: {str(e)}', 'error')
    
    return redirect(url_for('admin.updates'))

@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    """Eliminar mensaje"""
    try:
        message = NewsMessage.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()
        
        flash('Mensaje eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar mensaje: {str(e)}', 'error')
    
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/delete_selected', methods=['POST'])
@login_required
def delete_selected_messages():
    """Eliminar mensajes seleccionados"""
    try:
        message_ids = request.form.getlist('message_ids')
        if not message_ids:
            flash('No se seleccionaron mensajes para eliminar', 'warning')
            return redirect(url_for('admin.messages'))
        
        deleted_count = 0
        for message_id in message_ids:
            message = NewsMessage.query.get(message_id)
            if message:
                db.session.delete(message)
                deleted_count += 1
        
        db.session.commit()
        flash(f'{deleted_count} mensaje(s) eliminado(s) exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar mensajes: {str(e)}', 'error')
    
    return redirect(url_for('admin.messages'))

@admin_bp.route('/launcher/<int:launcher_id>/delete', methods=['POST'])
@login_required
def delete_launcher(launcher_id):
    """Eliminar versión del launcher"""
    try:
        launcher = LauncherVersion.query.get_or_404(launcher_id)
        
        # Verificar que no sea la versión actual
        if launcher.is_current:
            flash('No se puede eliminar la versión actual del launcher', 'error')
            return redirect(url_for('admin.launcher_versions'))
        
        # Eliminar archivo físico
        if os.path.exists(launcher.file_path):
            os.remove(launcher.file_path)
        
        # Eliminar registro de la base de datos
        db.session.delete(launcher)
        db.session.commit()
        
        flash(f'Launcher versión {launcher.version} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar launcher: {str(e)}', 'error')
    
    return redirect(url_for('admin.launcher_versions'))

@admin_bp.route('/logs/stats')
@login_required
def logs_stats():
    """API para estadísticas de logs en tiempo real"""
    try:
        from datetime import datetime, timedelta
        
        # Estadísticas de la última hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        last_hour_downloads = DownloadLog.query.filter(
            DownloadLog.created_at >= one_hour_ago
        ).count()
        
        last_hour_unique_ips = db.session.query(DownloadLog.ip_address).distinct().filter(
            DownloadLog.created_at >= one_hour_ago
        ).count()
        
        # Archivos más populares (últimas 24 horas)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        
        popular_files = db.session.query(
            DownloadLog.file_requested,
            db.func.count(DownloadLog.id).label('count')
        ).filter(
            DownloadLog.created_at >= twenty_four_hours_ago
        ).group_by(
            DownloadLog.file_requested
        ).order_by(
            db.func.count(DownloadLog.id).desc()
        ).limit(5).all()
        
        # Actividad por hora (últimas 24 horas)
        hourly_activity = []
        for i in range(24):
            hour_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            
            count = DownloadLog.query.filter(
                DownloadLog.created_at >= hour_start,
                DownloadLog.created_at < hour_end
            ).count()
            
            hourly_activity.append({
                'hour': hour_start.strftime('%H:00'),
                'count': count
            })
        
        return jsonify({
            'last_hour_downloads': last_hour_downloads,
            'last_hour_unique_ips': last_hour_unique_ips,
            'popular_files': [{'file': f[0], 'count': f[1]} for f in popular_files],
            'hourly_activity': list(reversed(hourly_activity))
        })
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estadísticas de logs: {e}")
        return jsonify({'error': str(e)}), 500