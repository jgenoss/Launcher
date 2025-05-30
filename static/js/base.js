/**
 * base.js - Archivo principal para Vue.js con SweetAlert2 y Axios
 * Configuración con delimitadores [[ ]] y Vue Mixins
 */

// ==================== CONFIGURACIÓN GLOBAL ====================

// Configurar Vue con delimitadores personalizados
Vue.config.delimiters = ['[[', ']]'];

// Configurar Axios globalmente
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// ==================== MIXINS REUTILIZABLES ====================

// Mixin para notificaciones con SweetAlert2
const NotificationMixin = {
    methods: {
        showSuccess(title, text = '') {
            Swal.fire({
                title: title,
                text: text,
                icon: 'success',
                timer: 3000,
                timerProgressBar: true,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        },
        
        showError(title, text = '') {
            Swal.fire({
                title: title,
                text: text,
                icon: 'error',
                confirmButtonText: 'Entendido'
            });
        },
        
        showWarning(title, text = '') {
            Swal.fire({
                title: title,
                text: text,
                icon: 'warning',
                confirmButtonText: 'OK'
            });
        },
        
        showInfo(title, text = '') {
            Swal.fire({
                title: title,
                text: text,
                icon: 'info',
                timer: 5000,
                timerProgressBar: true,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        },
        
        async showConfirmation(title, text = '', confirmText = 'Sí, continuar') {
            const result = await Swal.fire({
                title: title,
                text: text,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: confirmText,
                cancelButtonText: 'Cancelar',
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6'
            });
            return result.isConfirmed;
        },
        
        showLoading(title = 'Procesando...') {
            Swal.fire({
                title: title,
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        },
        
        hideLoading() {
            Swal.close();
        }
    }
};

// Mixin para peticiones HTTP con Axios
const HttpMixin = {
    methods: {
        async apiGet(url, params = {}) {
            try {
                const response = await axios.get(url, { params });
                return response.data;
            } catch (error) {
                this.handleHttpError(error);
                throw error;
            }
        },
        
        async apiPost(url, data = {}) {
            try {
                const response = await axios.post(url, data);
                return response.data;
            } catch (error) {
                this.handleHttpError(error);
                throw error;
            }
        },
        
        async apiPut(url, data = {}) {
            try {
                const response = await axios.put(url, data);
                return response.data;
            } catch (error) {
                this.handleHttpError(error);
                throw error;
            }
        },
        
        async apiDelete(url) {
            try {
                const response = await axios.delete(url);
                return response.data;
            } catch (error) {
                this.handleHttpError(error);
                throw error;
            }
        },
        
        async uploadFile(url, file, onProgress = null) {
            try {
                const formData = new FormData();
                formData.append('file', file);
                
                const config = {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                };
                
                if (onProgress) {
                    config.onUploadProgress = onProgress;
                }
                
                const response = await axios.post(url, formData, config);
                return response.data;
            } catch (error) {
                this.handleHttpError(error);
                throw error;
            }
        },
        
        handleHttpError(error) {
            console.error('HTTP Error:', error);
            
            if (error.response) {
                // Error del servidor
                const status = error.response.status;
                const message = error.response.data?.message || 'Error del servidor';
                
                switch (status) {
                    case 400:
                        this.showError('Error de solicitud', message);
                        break;
                    case 401:
                        this.showError('No autorizado', 'Sesión expirada. Inicia sesión nuevamente.');
                        setTimeout(() => window.location.href = '/login', 2000);
                        break;
                    case 403:
                        this.showError('Acceso denegado', 'No tienes permisos para realizar esta acción.');
                        break;
                    case 404:
                        this.showError('No encontrado', 'El recurso solicitado no existe.');
                        break;
                    case 500:
                        this.showError('Error interno', 'Error del servidor. Intenta nuevamente.');
                        break;
                    default:
                        this.showError('Error', message);
                }
            } else if (error.request) {
                // Error de red
                this.showError('Error de conexión', 'No se pudo conectar con el servidor.');
            } else {
                // Error de configuración
                this.showError('Error', 'Error inesperado.');
            }
        }
    }
};

// Mixin para utilidades comunes
const UtilsMixin = {
    methods: {
        formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        },
        
        formatDate(date) {
            return new Date(date).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showSuccess('Copiado', 'Texto copiado al portapapeles');
            }).catch(() => {
                this.showError('Error', 'No se pudo copiar al portapapeles');
            });
        },
        
        downloadFile(url, filename) {
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
};

// Mixin para SocketIO
const SocketMixin = {
    data() {
        return {
            socket: null,
            isSocketConnected: false
        };
    },
    
    methods: {
        initSocket(namespace = '/admin') {
            if (typeof io !== 'undefined') {
                this.socket = io(namespace);
                this.setupSocketEvents();
            }
        },
        
        setupSocketEvents() {
            if (!this.socket) return;
            
            this.socket.on('connect', () => {
                this.isSocketConnected = true;
                console.log('SocketIO conectado');
            });
            
            this.socket.on('disconnect', () => {
                this.isSocketConnected = false;
                console.log('SocketIO desconectado');
            });
            
            this.socket.on('notification', (data) => {
                this.handleSocketNotification(data);
            });
            
            this.socket.on('stats_update', (data) => {
                this.handleStatsUpdate(data);
            });
        },
        
        handleSocketNotification(data) {
            const { type, message } = data;
            
            switch (type) {
                case 'success':
                    this.showSuccess('Actualización', message);
                    break;
                case 'error':
                case 'danger':
                    this.showError('Error', message);
                    break;
                case 'warning':
                    this.showWarning('Advertencia', message);
                    break;
                default:
                    this.showInfo('Información', message);
            }
        },
        
        handleStatsUpdate(data) {
            // Override en componentes específicos
            console.log('Stats update:', data);
        },
        
        emitSocket(event, data) {
            if (this.socket && this.isSocketConnected) {
                this.socket.emit(event, data);
            }
        }
    }
};

// ==================== INSTANCIA PRINCIPAL DE VUE ====================

// Función para crear instancia Vue con mixins comunes
function createVueInstance(options = {}) {
    const defaultOptions = {
        el: '#app',
        mixins: [NotificationMixin, HttpMixin, UtilsMixin, SocketMixin],
        data() {
            return {
                loading: false,
                ...options.data || {}
            };
        },
        mounted() {
            this.initSocket();
            // Llamar mounted personalizado si existe
            if (options.mounted) {
                options.mounted.call(this);
            }
        },
        methods: {
            ...options.methods || {}
        },
        computed: {
            ...options.computed || {}
        },
        watch: {
            ...options.watch || {}
        }
    };
    
    return new Vue(defaultOptions);
}

// ==================== FUNCIONES GLOBALES DE UTILIDAD ====================

// Función global para mostrar notificaciones sin Vue
window.showNotification = {
    success: (title, text = '') => {
        Swal.fire({
            title: title,
            text: text,
            icon: 'success',
            timer: 3000,
            timerProgressBar: true,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
        });
    },
    
    error: (title, text = '') => {
        Swal.fire({
            title: title,
            text: text,
            icon: 'error',
            confirmButtonText: 'Entendido'
        });
    },
    
    warning: (title, text = '') => {
        Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            confirmButtonText: 'OK'
        });
    },
    
    info: (title, text = '') => {
        Swal.fire({
            title: title,
            text: text,
            icon: 'info',
            timer: 5000,
            timerProgressBar: true,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
        });
    }
};

// Función global para confirmaciones
window.showConfirmation = async (title, text = '', confirmText = 'Sí, continuar') => {
    const result = await Swal.fire({
        title: title,
        text: text,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: confirmText,
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6'
    });
    return result.isConfirmed;
};

// Exponer funciones para uso global
window.createVueInstance = createVueInstance;
window.NotificationMixin = NotificationMixin;
window.HttpMixin = HttpMixin;
window.UtilsMixin = UtilsMixin;
window.SocketMixin = SocketMixin;

// ==================== AUTO-INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', function() {
    // Ocultar alertas automáticamente después de 5 segundos
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.realtime-notification)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    console.log('Base.js cargado correctamente');
});