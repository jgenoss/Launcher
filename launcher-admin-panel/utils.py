import os
import hashlib
import zipfile
from datetime import datetime
from functools import wraps
from flask import current_app, flash, request,redirect, url_for
from werkzeug.utils import secure_filename
import shutil
import json

def calculate_file_hash(file_path, algorithm='md5'):
    """Calcular hash de un archivo"""
    hash_algo = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_algo.update(chunk)
        return hash_algo.hexdigest()
    except Exception as e:
        current_app.logger.error(f"Error calculating {algorithm} for {file_path}: {e}")
        return None

def allowed_file(filename, file_type='file'):
    """Verificar si el archivo tiene una extensión permitida"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {})
    
    return extension in allowed_extensions.get(file_type, set())

def get_file_size_mb(file_path):
    """Obtener tamaño de archivo en MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0

def format_file_size(size_bytes):
    """Formatear tamaño de archivo en formato legible"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"

def validate_version_format(version_string):
    """Validar formato de versión (X.Y.Z.W)"""
    try:
        parts = version_string.split('.')
        if len(parts) != 4:
            return False
        
        # Verificar que todas las partes sean números
        for part in parts:
            int(part)
        
        return True
    except:
        return False

def compare_versions(version1, version2):
    """Comparar dos versiones. Retorna -1, 0, 1"""
    try:
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Rellenar con ceros si es necesario
        while len(v1_parts) < 4:
            v1_parts.append(0)
        while len(v2_parts) < 4:
            v2_parts.append(0)
        
        for i in range(4):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    except:
        return 0

def create_zip_archive(source_path, zip_path, exclude_patterns=None):
    """Crear archivo ZIP desde un directorio"""
    exclude_patterns = exclude_patterns or []
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(source_path):
                # Si es un archivo individual
                zipf.write(source_path, os.path.basename(source_path))
            else:
                # Si es un directorio
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, source_path)
                        
                        # Verificar patrones de exclusión
                        should_exclude = False
                        for pattern in exclude_patterns:
                            if pattern in relative_path:
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            zipf.write(file_path, relative_path)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error creating ZIP archive: {e}")
        return False

def extract_zip_archive(zip_path, extract_to, overwrite=True):
    """Extraer archivo ZIP"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Verificar integridad del ZIP
            if zipf.testzip() is not None:
                raise Exception("ZIP file is corrupted")
            
            # Crear directorio de destino si no existe
            os.makedirs(extract_to, exist_ok=True)
            
            # Extraer archivos
            for member in zipf.infolist():
                # Prevenir path traversal attacks
                if ".." in member.filename or member.filename.startswith("/"):
                    continue
                
                target_path = os.path.join(extract_to, member.filename)
                
                # Verificar si el archivo ya existe
                if os.path.exists(target_path) and not overwrite:
                    continue
                
                # Crear directorios padre si es necesario
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Extraer archivo
                with zipf.open(member) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error extracting ZIP archive: {e}")
        return False

def safe_delete_file(file_path):
    """Eliminar archivo de forma segura"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error deleting file {file_path}: {e}")
        return False

def safe_delete_directory(dir_path):
    """Eliminar directorio de forma segura"""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error deleting directory {dir_path}: {e}")
        return False

def backup_file(file_path, backup_dir=None):
    """Crear backup de un archivo"""
    try:
        if not os.path.exists(file_path):
            return None
        
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{timestamp}_{filename}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        current_app.logger.error(f"Error creating backup for {file_path}: {e}")
        return None

def cleanup_old_backups(backup_dir, max_age_days=30):
    """Limpiar backups antiguos"""
    try:
        if not os.path.exists(backup_dir):
            return 0
        
        current_time = datetime.now()
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            if os.path.isfile(file_path):
                file_age = datetime.fromtimestamp(os.path.getctime(file_path))
                age_days = (current_time - file_age).days
                
                if age_days > max_age_days:
                    os.remove(file_path)
                    deleted_count += 1
        
        return deleted_count
    except Exception as e:
        current_app.logger.error(f"Error cleaning up backups: {e}")
        return 0

def validate_json_file(file_path):
    """Validar que un archivo JSON sea válido"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except:
        return False

def create_directory_structure(base_path, structure):
    """Crear estructura de directorios"""
    try:
        for path in structure:
            full_path = os.path.join(base_path, path)
            os.makedirs(full_path, exist_ok=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Error creating directory structure: {e}")
        return False

def log_user_action(user_id, action, details=None):
    """Registrar acción del usuario"""
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # Aquí podrías guardar en base de datos o archivo de log
        current_app.logger.info(f"User action: {json.dumps(log_entry)}")
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error logging user action: {e}")
        return False

def generate_update_json(version, updates, file_hashes):
    """Generar JSON de actualización para el launcher"""
    try:
        update_data = {
            "latest_version": version,
            "updates": updates,
            "file_hashes": file_hashes
        }
        
        return json.dumps(update_data, indent=2)
    except Exception as e:
        current_app.logger.error(f"Error generating update JSON: {e}")
        return None

def generate_launcher_json(version, filename):
    """Generar JSON de información del launcher"""
    try:
        launcher_data = {
            "version": version,
            "file_name": filename
        }
        
        return json.dumps(launcher_data, indent=2)
    except Exception as e:
        current_app.logger.error(f"Error generating launcher JSON: {e}")
        return None

def validate_md5_hash(hash_string):
    """Validar formato de hash MD5"""
    if not hash_string or len(hash_string) != 32:
        return False
    
    try:
        int(hash_string, 16)
        return True
    except ValueError:
        return False

def get_disk_usage(path):
    """Obtener uso de disco"""
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total,
            'used': used,
            'free': free,
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'usage_percent': round((used / total) * 100, 1)
        }
    except Exception as e:
        current_app.logger.error(f"Error getting disk usage: {e}")
        return None

def sanitize_filename(filename):
    """Sanitizar nombre de archivo"""
    # Usar secure_filename de Werkzeug y agregar validaciones adicionales
    filename = secure_filename(filename)
    
    # Remover caracteres problemáticos adicionales
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        
        if not current_user.is_admin:
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('admin.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

class FileManager:
    """Clase para gestionar archivos de forma más organizada"""
    
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save_file(self, file, subdirectory=''):
        """Guardar archivo en el directorio especificado"""
        try:
            if subdirectory:
                save_path = os.path.join(self.base_path, subdirectory)
            else:
                save_path = self.base_path
            
            os.makedirs(save_path, exist_ok=True)
            
            filename = sanitize_filename(file.filename)
            file_path = os.path.join(save_path, filename)
            
            file.save(file_path)
            return file_path
        except Exception as e:
            current_app.logger.error(f"Error saving file: {e}")
            return None
    
    def delete_file(self, filename, subdirectory=''):
        """Eliminar archivo"""
        try:
            if subdirectory:
                file_path = os.path.join(self.base_path, subdirectory, filename)
            else:
                file_path = os.path.join(self.base_path, filename)
            
            return safe_delete_file(file_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, filename, subdirectory=''):
        """Obtener información de un archivo"""
        try:
            if subdirectory:
                file_path = os.path.join(self.base_path, subdirectory, filename)
            else:
                file_path = os.path.join(self.base_path, filename)
            
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'name': filename,
                'size': stat.st_size,
                'size_formatted': format_file_size(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'md5': calculate_file_hash(file_path, 'md5')
            }
        except Exception as e:
            current_app.logger.error(f"Error getting file info: {e}")
            return None