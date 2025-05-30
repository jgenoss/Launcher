/**
 * files.js - Lógica Vue.js para gestión de archivos del juego
 * Ahora carga todos los datos vía API.
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
        // Asegurarse de que al menos las URLs y versions estén inicializadas si se cargan por separado.
        window.FILES_DATA = {
            files: [],
            versions: [],
            currentVersionId: null,
            urls: {
                deleteFile: '',
                deleteSelected: '',
                downloadBase: ''
            }
        };
    }
    
    console.log('✅ Todas las dependencias disponibles');
    console.log('📁 Datos de archivos iniciales (desde HTML):', window.FILES_DATA);
    
    // Configurar delimitadores de Vue
    Vue.config.delimiters = ['[[', ']]'];
    
    // Crear instancia Vue para Files
    const filesApp = new Vue({
        el: '#app',
        delimiters: ['[[', ']]'],
        mixins: [NotificationMixin, HttpMixin, UtilsMixin, SocketMixin],
        
        data() {
            return {
                // Datos que se cargarán vía API
                files: [], // Inicialmente vacío, se llenará con la llamada API
                
                // Datos del servidor (se obtienen del HTML inicial o API separada)
                versions: window.FILES_DATA.versions || [], // Para el dropdown de filtro
                currentVersionId: window.FILES_DATA.currentVersionId || null,
                urls: window.FILES_DATA.urls || {},
                
                // Filtros (se mantienen en el cliente)
                filters: {
                    search: '',
                    extension: '',
                    size: '',
                    page: 1, // Controla la paginación a nivel de API
                    per_page: 50, // Controla la paginación a nivel de API
                },
                
                // Paginación (ahora reflejará la API)
                pagination: {
                    page: 1,
                    pages: 1,
                    perPage: 50,
                    total: 0,
                    hasNext: false,
                    hasPrev: false
                },

                // Selección
                selectedFiles: [],
                selectAllChecked: false,
                
                // Modal
                selectedFile: {},
                
                // Estados
                loading: false, // Controla el overlay de carga global
                loadingData: false, // Específico para la carga de datos de archivos
                loadingMessage: 'Cargando...',
                deleting: false,
                
                // SocketIO (gestionado por SocketMixin)
                isSocketConnected: false,
                socket: null
            };
        },
        
        computed: {
            /**
             * Archivos filtrados localmente (solo por búsqueda, extensión, tamaño, paginación viene de la API)
             */
            filteredFiles() {
                // Si la API ya devuelve paginado y filtrado por versión, aquí solo se aplica
                // búsqueda, extensión y tamaño si es necesario aplicarlos client-side adicionalmente.
                // En este modelo, el backend hace la mayor parte del filtrado y paginación.
                let result = [...this.files]; // 'files' ya viene paginado y filtrado por version_id

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
             * Total de páginas (ahora de la API)
             */
            totalPages() {
                return this.pagination.pages;
            },
            
            /**
             * Páginas visibles en paginación (basado en totalPages de la API)
             */
            visiblePages() {
                const total = this.pagination.pages;
                const current = this.pagination.page;
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
             * Índices para mostrar en paginación (ahora de la API)
             */
            startIndex() {
                if (this.pagination.total === 0) return 0;
                return (this.pagination.page - 1) * this.pagination.perPage + 1;
            },
            
            endIndex() {
                if (this.pagination.total === 0) return 0;
                const end = this.pagination.page * this.pagination.perPage;
                return Math.min(end, this.pagination.total);
            },
            
            /**
             * Estadísticas de archivos (ahora basadas en 'files' directamente de la API, y filtrado local)
             */
            statistics() {
                const totalSize = this.files.reduce((sum, file) => sum + (file.file_size || 0), 0);
                const withMD5 = this.files.filter(file => file.md5_hash).length;
                
                // Cuando el currentVersionId está seteado en el HTML, significa que la API ya devuelve archivos filtrados por esa versión.
                // Entonces, 'totalFiles' es el total filtrado para esa versión, y 'filteredFiles' será el total de la paginación actual.
                const totalFilesCount = this.pagination.total; // Total de archivos para el filtro de versión actual
                const filesInCurrentPage = this.filteredFiles.length; // Archivos después de filtros locales (search, ext, size)
                
                return {
                    totalFiles: totalFilesCount, // Renombrado de statistics.totalFiles a totalFilesCount
                    totalSizeFormatted: this.formatFileSize(totalSize),
                    filteredFiles: filesInCurrentPage, // Total de elementos en la vista actual después de filtros locales
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
            
            // Inicializar SocketIO
            this.initSocket();
            
            // Cargar datos de archivos desde la API
            this.loadFilesData();

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
             * Cargar datos de archivos desde la API con los filtros actuales
             */
            async loadFilesData() {
                this.loadingData = true; // Iniciar carga de datos específica de la tabla
                this.selectedFiles = []; // Limpiar selección al recargar datos
                this.updateSelectAllState(); // Actualizar estado de "seleccionar todo"

                try {
                    const params = {
                        page: this.filters.page,
                        per_page: this.filters.per_page,
                        version_id: this.currentVersionId // Pasar el filtro de versión si existe
                        // Los filtros de búsqueda, extensión y tamaño se aplicarán client-side a 'files'
                        // una vez que los datos son recibidos. O se pueden pasar a la API si el backend los soporta.
                    };

                    const response = await this.apiGet('/admin/api/files_data', params);
                    this.files = response.files; // Asignar los archivos recibidos
                    this.pagination = response.pagination; // Actualizar datos de paginación
                    // Asegurarse de que las URLs se obtengan si no vienen del HTML inicial, o mantenerlas como en HTML
                    // this.urls = response.urls; 

                    console.log('✅ Archivos cargados desde API:', this.files.length);
                } catch (error) {
                    this.showError('Error', 'No se pudieron cargar los archivos.');
                    console.error('Error loading files data:', error);
                } finally {
                    this.loadingData = false; // Finalizar carga de datos
                }
            },

            /**
             * Aplicar filtros (debounced para búsqueda) y recargar datos de la API si es necesario
             */
            applyFilters() {
                // Al cambiar filtros como search, extension, size, la paginación debe resetearse a 1
                this.filters.page = 1;
                // Si el filtro de versión cambia (desde el dropdown de Flask), la página se recargaría,
                // así que esta función solo aplica los filtros locales (search, extension, size).
                this.updateSelection(); // Re-evaluar selección
            },
            
            /**
             * Cambiar página y recargar datos de la API
             */
            changePage(page) {
                if (page >= 1 && page <= this.pagination.pages && page !== this.pagination.page) {
                    this.filters.page = page;
                    this.loadFilesData(); // Volver a cargar datos para la nueva página
                }
            },
            
            /**
             * Seleccionar/deseleccionar todos los archivos visibles en la página actual
             */
            selectAll() {
                if (this.selectedFiles.length === this.filteredFiles.map(file => file.id).filter(id => this.selectedFiles.includes(id)).length) {
                    // Si todos los archivos filtrados actualmente visibles están seleccionados, deseleccionar todos
                    this.selectedFiles = [];
                } else {
                    // De lo contrario, seleccionar todos los archivos filtrados actualmente visibles
                    this.selectedFiles = this.filteredFiles.map(file => file.id);
                }
                this.updateSelectAllState();
            },
            
            /**
             * Toggle select all checkbox
             */
            toggleSelectAll() {
                if (this.selectAllChecked) {
                    this.selectedFiles = this.filteredFiles.map(file => file.id);
                } else {
                    this.selectedFiles = [];
                }
            },
            
            /**
             * Actualizar estado de selección
             */
            updateSelection() {
                // No es necesario filtrar selectedFiles aquí, ya que la selección se maneja a nivel de UI
                // y se limpiará o actualizará al cargar nuevos datos.
                this.updateSelectAllState();
            },
            
            /**
             * Actualizar estado del checkbox "Seleccionar todo"
             */
            updateSelectAllState() {
                const visibleIds = this.filteredFiles.map(file => file.id);
                const selectedOnPage = this.selectedFiles.filter(id => visibleIds.includes(id));
                
                this.selectAllChecked = visibleIds.length > 0 && selectedOnPage.length === visibleIds.length;
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
                    // Usar Axios para la solicitud POST
                    await this.apiPost(this.urls.deleteFile.replace('0', file.id));
                    
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
                    
                    // Recargar datos para actualizar paginación y estadísticas si el total cambia
                    // No es estrictamente necesario si solo se actualiza 'files' localmente y se tiene una API de stats separada.
                    // Pero si la paginación es compleja o las estadísticas deben ser exactas al instante, recargar puede ser mejor.
                    this.loadFilesData(); // Recargar datos para reflejar cambios en el total/páginas

                } catch (error) {
                    console.error('Error eliminando archivo:', error);
                    // handleHttpError en HttpMixin ya muestra el error.
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
                    
                    // Usar Axios para la solicitud POST de FormData
                    await axios.post(this.urls.deleteSelected, formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data' // Asegurar el tipo de contenido para FormData
                        }
                    });
                    
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

                    this.loadFilesData(); // Recargar datos para reflejar cambios en el total/páginas
                    
                } catch (error) {
                    console.error('Error eliminando archivos:', error);
                    // handleHttpError en HttpMixin ya muestra el error.
                } finally {
                    this.deleting = false;
                }
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
                            this.showInfo('Archivos actualizados', 'Se han subido nuevos archivos. Recargando lista...');
                            this.loadFilesData(); // Recargar la lista de archivos para mostrar los nuevos
                            break;
                            
                        case 'file_deleted':
                            // Otro usuario eliminó un archivo, actualizar localmente y quizás recargar
                            if (data.data.filename) {
                                this.showInfo('Archivo eliminado', `${data.data.filename} fue eliminado por otro usuario. Recargando lista...`);
                            }
                            this.loadFilesData(); // Recargar para sincronizar la lista
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
                handler: function(newVal, oldVal) {
                    // Debounce para búsqueda
                    this.debounce(this.loadFilesData, 300)();
                }
            },
            
            'filters.extension': function() {
                this.loadFilesData(); // Recargar al cambiar extensión
            },
            
            'filters.size': function() {
                this.loadFilesData(); // Recargar al cambiar tamaño
            },
            
            /**
             * Observar cambios en selectedFiles para actualizar selectAll
             */
            selectedFiles: {
                handler() {
                    this.updateSelectAllState();
                },
                deep: true
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