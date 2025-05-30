/**
 * files.js - Lógica Vue.js para gestión de archivos del juego
 * Separado completamente del template HTML
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOMContentLoaded - Iniciando Files Vue.js');
    
    // Verificaciones de dependencias
    if (typeof Vue === 'undefined') {
        console.error('❌ Vue.js no está disponible');
        return;
    }
    
    const appElement = document.getElementById('app');
    if (!appElement) {
        console.error('❌ Elemento #app no encontrado en el DOM');
        return;
    }
    
    if (typeof NotificationMixin === 'undefined') {
        console.error('❌ Mixins no están disponibles');
        return;
    }
    
    // Verificar datos del servidor
    if (typeof window.FILES_DATA === 'undefined') {
        console.error('❌ FILES_DATA no está disponible');
        return;
    }
    
    console.log('✅ Todas las dependencias disponibles');
    console.log('📁 Datos de archivos:', window.FILES_DATA);
    
    // Configurar delimitadores de Vue
    Vue.config.delimiters = ['[[', ']]'];
    
    // Crear instancia Vue para Files
    const filesApp = new Vue({
        el: '#app',
        delimiters: ['[[', ']]'],
        mixins: [NotificationMixin, HttpMixin, UtilsMixin, SocketMixin],
        
        data() {
            return {
                // Datos del servidor
                files: window.FILES_DATA.files || [],
                versions: window.FILES_DATA.versions || [],
                currentVersionId: window.FILES_DATA.currentVersionId || null,
                urls: window.FILES_DATA.urls || {},
                
                // Filtros
                filters: {
                    search: '',
                    extension: '',
                    size: ''
                },
                
                // Paginación local
                currentPage: 1,
                itemsPerPage: 50,
                
                // Selección
                selectedFiles: [],
                selectAllChecked: false,
                
                // Modal
                selectedFile: {},
                
                // Estados
                loading: false,
                loadingMessage: 'Cargando...',
                deleting: false,
                
                // SocketIO
                isSocketConnected: false,
                socket: null
            };
        },
        
        computed: {
            /**
             * Archivos filtrados según criterios de búsqueda
             */
            filteredFiles() {
                let result = [...this.files];
                
                // Filtro por búsqueda (nombre, ruta, hash)
                if (this.filters.search) {
                    const search = this.filters.search.toLowerCase();
                    result = result.filter(file => 
                        file.filename.toLowerCase().includes(search) ||
                        file.relative_path.toLowerCase().includes(search) ||
                        (file.md5_hash && file.md5_hash.toLowerCase().includes(search))
                    );
                }
                
                // Filtro por extensión
                if (this.filters.extension) {
                    result = result.filter(file => 
                        file.filename.toLowerCase().endsWith(this.filters.extension)
                    );
                }
                
                // Filtro por tamaño
                if (this.filters.size && this.filters.size !== '') {
                    result = result.filter(file => {
                        if (!file.file_size) return false;
                        
                        const sizeMB = file.file_size / (1024 * 1024);
                        switch (this.filters.size) {
                            case 'small': return sizeMB < 1;
                            case 'medium': return sizeMB >= 1 && sizeMB <= 10;
                            case 'large': return sizeMB > 10;
                            default: return true;
                        }
                    });
                }
                
                return result;
            },
            
            /**
             * Archivos para la página actual
             */
            paginatedFiles() {
                const start = (this.currentPage - 1) * this.itemsPerPage;
                const end = start + this.itemsPerPage;
                return this.filteredFiles.slice(start, end);
            },
            
            /**
             * Total de páginas
             */
            totalPages() {
                return Math.ceil(this.filteredFiles.length / this.itemsPerPage);
            },
            
            /**
             * Páginas visibles en paginación
             */
            visiblePages() {
                const total = this.totalPages;
                const current = this.currentPage;
                const pages = [];
                
                if (total <= 7) {
                    for (let i = 1; i <= total; i++) {
                        pages.push(i);
                    }
                } else {
                    if (current <= 4) {
                        for (let i = 1; i <= 5; i++) pages.push(i);
                        pages.push('...');
                        pages.push(total);
                    } else if (current >= total - 3) {
                        pages.push(1);
                        pages.push('...');
                        for (let i = total - 4; i <= total; i++) pages.push(i);
                    } else {
                        pages.push(1);
                        pages.push('...');
                        for (let i = current - 1; i <= current + 1; i++) pages.push(i);
                        pages.push('...');
                        pages.push(total);
                    }
                }
                
                return pages;
            },
            
            /**
             * Índices para mostrar en paginación
             */
            startIndex() {
                return (this.currentPage - 1) * this.itemsPerPage + 1;
            },
            
            endIndex() {
                const end = this.currentPage * this.itemsPerPage;
                return Math.min(end, this.filteredFiles.length);
            },
            
            /**
             * Estadísticas de archivos
             */
            statistics() {
                const totalSize = this.files.reduce((sum, file) => sum + (file.file_size || 0), 0);
                const withMD5 = this.files.filter(file => file.md5_hash).length;
                const filteredCount = this.currentVersionId ? 
                    this.files.filter(file => file.version_id === this.currentVersionId).length :
                    this.versions.length;
                
                return {
                    totalFiles: this.files.length,
                    totalSizeFormatted: this.formatFileSize(totalSize),
                    filteredFiles: filteredCount,
                    withMD5: withMD5
                };
            },
            
            /**
             * Nombre de la versión actual filtrada
             */
            currentVersionName() {
                if (!this.currentVersionId) return null;
                const version = this.versions.find(v => v.id === this.currentVersionId);
                return version ? version.version : null;
            }
        },
        
        mounted() {
            console.log('✅ Files Vue montado');
            console.log('📊 Estadísticas iniciales:', this.statistics);
            
            // Inicializar SocketIO
            this.initSocket();
            
            // Auto-focus en búsqueda
            this.$nextTick(() => {
                const searchInput = this.$el.querySelector('input[placeholder*="Buscar"]');
                if (searchInput) {
                    searchInput.focus();
                }
            });
            
            console.log('Files management inicializado correctamente');
        },
        
        methods: {
            /**
             * Aplicar filtros (debounced para búsqueda)
             */
            applyFilters() {
                // Reset página al filtrar
                this.currentPage = 1;
                
                // Update selección
                this.updateSelection();
                
                console.log('Filtros aplicados:', this.filters);
                console.log('Archivos filtrados:', this.filteredFiles.length);
            },
            
            /**
             * Cambiar página
             */
            changePage(page) {
                if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
                    this.currentPage = page;
                    this.updateSelection();
                }
            },
            
            /**
             * Seleccionar/deseleccionar todos
             */
            selectAll() {
                if (this.selectedFiles.length === this.paginatedFiles.length) {
                    this.selectedFiles = [];
                } else {
                    this.selectedFiles = this.paginatedFiles.map(file => file.id);
                }
                this.updateSelectAllState();
            },
            
            /**
             * Toggle select all checkbox
             */
            toggleSelectAll() {
                if (this.selectAllChecked) {
                    this.selectedFiles = this.paginatedFiles.map(file => file.id);
                } else {
                    this.selectedFiles = [];
                }
            },
            
            /**
             * Actualizar estado de selección
             */
            updateSelection() {
                // Filtrar selección para mantener solo archivos visibles
                const visibleIds = this.paginatedFiles.map(file => file.id);
                this.selectedFiles = this.selectedFiles.filter(id => visibleIds.includes(id));
                this.updateSelectAllState();
            },
            
            /**
             * Actualizar estado del checkbox "Seleccionar todo"
             */
            updateSelectAllState() {
                const visibleCount = this.paginatedFiles.length;
                const selectedCount = this.selectedFiles.length;
                
                this.selectAllChecked = visibleCount > 0 && selectedCount === visibleCount;
            },
            
            /**
             * Obtener icono según extensión de archivo
             */
            getFileIcon(filename) {
                const ext = this.getFileExtension(filename).toLowerCase();
                const icons = {
                    '.exe': 'bi bi-app text-primary',
                    '.dll': 'bi bi-gear text-secondary',
                    '.xml': 'bi bi-code text-info',
                    '.json': 'bi bi-code text-info',
                    '.txt': 'bi bi-file-text text-success',
                    '.png': 'bi bi-image text-warning',
                    '.jpg': 'bi bi-image text-warning',
                    '.gif': 'bi bi-image text-warning'
                };
                
                return icons[ext] || 'bi bi-file-earmark text-muted';
            },
            
            /**
             * Obtener extensión de archivo
             */
            getFileExtension(filename) {
                const lastDot = filename.lastIndexOf('.');
                return lastDot > 0 ? filename.substring(lastDot) : '';
            },
            
            /**
             * Mostrar detalles de archivo en modal
             */
            showFileDetails(file) {
                this.selectedFile = { ...file };
                
                // Mostrar modal usando Bootstrap
                const modal = new bootstrap.Modal(document.getElementById('fileDetailModal'));
                modal.show();
            },
            
            /**
             * Descargar archivo
             */
            downloadFile(filename) {
                const url = `${this.urls.downloadBase}${filename}`;
                window.open(url, '_blank');
                
                this.showInfo('Descarga iniciada', `Descargando ${filename}`);
            },
            
            /**
             * Eliminar archivo individual
             */
            async deleteFile(file) {
                const confirmed = await this.showConfirmation(
                    '¿Eliminar archivo?',
                    `¿Estás seguro de que quieres eliminar "${file.filename}"? Esta acción no se puede deshacer.`,
                    'Sí, eliminar'
                );
                
                if (!confirmed) return;
                
                this.deleting = true;
                
                try {
                    const response = await fetch(this.urls.deleteFile.replace('0', file.id), {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        }
                    });
                    
                    if (response.ok) {
                        // Remover archivo de la lista local
                        this.files = this.files.filter(f => f.id !== file.id);
                        
                        // Remover de selección si estaba seleccionado
                        this.selectedFiles = this.selectedFiles.filter(id => id !== file.id);
                        
                        this.showSuccess('Archivo eliminado', `${file.filename} ha sido eliminado exitosamente`);
                        
                        // Emitir evento SocketIO
                        if (this.isSocketConnected) {
                            this.emitSocket('file_deleted', {
                                filename: file.filename,
                                version_id: file.version_id
                            });
                        }
                        
                    } else {
                        throw new Error(`Error del servidor: ${response.status}`);
                    }
                    
                } catch (error) {
                    console.error('Error eliminando archivo:', error);
                    this.showError('Error al eliminar', 'No se pudo eliminar el archivo');
                } finally {
                    this.deleting = false;
                }
            },
            
            /**
             * Eliminar archivos seleccionados
             */
            async deleteSelectedFiles() {
                if (this.selectedFiles.length === 0) {
                    this.showWarning('Sin selección', 'No hay archivos seleccionados para eliminar');
                    return;
                }
                
                const count = this.selectedFiles.length;
                const confirmed = await this.showConfirmation(
                    '¿Eliminar archivos seleccionados?',
                    `¿Estás seguro de que quieres eliminar ${count} archivo${count > 1 ? 's' : ''}? Esta acción no se puede deshacer.`,
                    'Sí, eliminar todos'
                );
                
                if (!confirmed) return;
                
                this.deleting = true;
                
                try {
                    const formData = new FormData();
                    this.selectedFiles.forEach(id => {
                        formData.append('file_ids', id);
                    });
                    
                    const response = await fetch(this.urls.deleteSelected, {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        // Remover archivos de la lista local
                        this.files = this.files.filter(file => !this.selectedFiles.includes(file.id));
                        
                        // Limpiar selección
                        this.selectedFiles = [];
                        this.updateSelectAllState();
                        
                        this.showSuccess(
                            'Archivos eliminados', 
                            `${count} archivo${count > 1 ? 's han' : ' ha'} sido eliminado${count > 1 ? 's' : ''} exitosamente`
                        );
                        
                        // Emitir evento SocketIO
                        if (this.isSocketConnected) {
                            this.emitSocket('files_deleted', { count });
                        }
                        
                    } else {
                        throw new Error(`Error del servidor: ${response.status}`);
                    }
                    
                } catch (error) {
                    console.error('Error eliminando archivos:', error);
                    this.showError('Error al eliminar', 'No se pudieron eliminar los archivos seleccionados');
                } finally {
                    this.deleting = false;
                }
            },
            
            /**
             * Formatear fecha para mostrar
             */
            formatDate(dateString) {
                if (!dateString) return 'N/A';
                
                const date = new Date(dateString);
                return date.toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit'
                });
            },
            
            /**
             * Manejar notificaciones desde SocketIO
             */
            handleSocketNotification(data) {
                // Llamar al método padre
                SocketMixin.methods.handleSocketNotification.call(this, data);
                
                // Manejar notificaciones específicas
                if (data.data && data.data.action) {
                    switch (data.data.action) {
                        case 'files_uploaded':
                            this.showInfo('Archivos actualizados', 'Se han subido nuevos archivos');
                            // Aquí podrías recargar la lista si es necesario
                            break;
                            
                        case 'file_deleted':
                            // Otro usuario eliminó un archivo
                            if (data.data.filename) {
                                this.showInfo('Archivo eliminado', `${data.data.filename} fue eliminado por otro usuario`);
                            }
                            break;
                    }
                }
            },
            
            /**
             * Establecer estado de carga global
             */
            setLoading(isLoading, message = 'Cargando...') {
                this.loading = isLoading;
                this.loadingMessage = message;
            },
            
            /**
             * Probar conexión SocketIO
             */
            testSocketConnection() {
                if (this.isSocketConnected) {
                    this.emitSocket('ping');
                    this.showInfo('Test SocketIO', 'Ping enviado al servidor');
                } else {
                    this.showWarning('Sin conexión', 'SocketIO no está conectado');
                }
            }
        },
        
        watch: {
            /**
             * Observar cambios en filtros para reset paginación
             */
            'filters.search': {
                handler() {
                    // Debounce para búsqueda
                    clearTimeout(this.searchTimeout);
                    this.searchTimeout = setTimeout(() => {
                        this.applyFilters();
                    }, 300);
                }
            },
            
            'filters.extension'() {
                this.applyFilters();
            },
            
            'filters.size'() {
                this.applyFilters();
            },
            
            /**
             * Observar cambios en selectedFiles para actualizar selectAll
             */
            selectedFiles: {
                handler() {
                    this.updateSelectAllState();
                },
                deep: true
            },
            
            /**
             * Observar cambios en filteredFiles para ajustar paginación
             */
            filteredFiles() {
                // Si la página actual no existe después del filtrado, ir a la primera
                if (this.currentPage > this.totalPages && this.totalPages > 0) {
                    this.currentPage = 1;
                }
            }
        }
    });
    
    // Exponer para debugging en desarrollo
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.filesApp = filesApp;
        console.log('✅ Files app disponible en window.filesApp para debugging');
    }
    
    console.log('✅ Files Vue.js inicializado exitosamente');
});