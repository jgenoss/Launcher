/**
 * create_version.js - Lógica Vue.js para crear nueva versión
 * Separado completamente del template HTML
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOMContentLoaded - Iniciando Create Version Vue.js');
    
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
    
    console.log('✅ Todas las dependencias disponibles');
    
    // Configurar delimitadores de Vue
    Vue.config.delimiters = ['[[', ']]'];
    
    // Crear instancia Vue para Create Version
    const createVersionApp = new Vue({
        el: '#app',
        delimiters: ['[[', ']]'],
        mixins: [NotificationMixin, HttpMixin, UtilsMixin, SocketMixin],
        
        data() {
            return {
                // Formulario
                form: {
                    version: '',
                    isLatest: true,
                    releaseNotes: ''
                },
                
                // Estados
                submitting: false,
                versionError: '',
                
                // Vista previa
                preview: {
                    version: '1.0.0.0',
                    status: 'Actual',
                    badgeClass: 'bg-success',
                    date: '',
                    notes: '',
                    notesFormatted: ''
                },
                
                // SocketIO
                isSocketConnected: false,
                socket: null,
                
                // Loading global
                loading: false,
                loadingMessage: 'Cargando...'
            };
        },
        
        computed: {
            /**
             * Verificar si el formulario es válido
             */
            isFormValid() {
                return this.form.version.trim() !== '' && 
                       this.isValidVersionFormat(this.form.version) && 
                       !this.versionError;
            }
        },
        
        mounted() {
            console.log('✅ Create Version Vue montado');
            
            // Inicializar SocketIO
            this.initSocket();
            
            // Configurar fecha actual
            this.preview.date = new Date().toLocaleDateString('es-ES');
            
            // Focus en el campo de versión
            this.$nextTick(() => {
                const versionInput = this.$el.querySelector('input[type="text"]');
                if (versionInput) {
                    versionInput.focus();
                }
            });
            
            console.log('Create Version inicializado correctamente');
        },
        
        methods: {
            /**
             * Validar formato de versión X.Y.Z.W
             * @param {string} version - Versión a validar
             * @returns {boolean}
             */
            isValidVersionFormat(version) {
                if (!version) return false;
                
                const versionPattern = /^\d+\.\d+\.\d+\.\d+$/;
                return versionPattern.test(version.trim());
            },
            
            /**
             * Auto-completar versión en evento blur
             */
            autoCompleteVersion() {
                let version = this.form.version.trim();
                
                if (version && !this.isValidVersionFormat(version)) {
                    const parts = version.split('.');
                    
                    // Completar con ceros hasta tener 4 partes
                    while (parts.length < 4) {
                        parts.push('0');
                    }
                    
                    // Tomar solo las primeras 4 partes
                    this.form.version = parts.slice(0, 4).join('.');
                    this.updatePreview();
                }
                
                this.validateVersion();
            },
            
            /**
             * Validar la versión ingresada
             */
            validateVersion() {
                const version = this.form.version.trim();
                
                if (!version) {
                    this.versionError = '';
                    return;
                }
                
                if (!this.isValidVersionFormat(version)) {
                    this.versionError = 'El formato debe ser: MAYOR.MENOR.PARCHE.BUILD (ej: 1.0.0.0)';
                    return;
                }
                
                // Validar que no sean todos ceros
                if (version === '0.0.0.0') {
                    this.versionError = 'La versión no puede ser 0.0.0.0';
                    return;
                }
                
                // Validar que las partes sean números válidos
                const parts = version.split('.');
                for (let part of parts) {
                    const num = parseInt(part);
                    if (isNaN(num) || num < 0 || num > 9999) {
                        this.versionError = 'Cada parte debe ser un número entre 0 y 9999';
                        return;
                    }
                }
                
                this.versionError = '';
            },
            
            /**
             * Actualizar vista previa en tiempo real
             */
            updatePreview() {
                // Actualizar versión
                this.preview.version = this.form.version || '1.0.0.0';
                
                // Actualizar estado
                if (this.form.isLatest) {
                    this.preview.status = 'Actual';
                    this.preview.badgeClass = 'bg-success';
                } else {
                    this.preview.status = 'Archivada';
                    this.preview.badgeClass = 'bg-secondary';
                }
                
                // Actualizar notas
                this.preview.notes = this.form.releaseNotes.trim();
                this.preview.notesFormatted = this.preview.notes.replace(/\n/g, '<br>');
                
                // Validar versión
                this.validateVersion();
            },
            
            /**
             * Enviar formulario para crear versión
             */
            async submitVersion() {
                console.log('Enviando formulario de versión...');
                
                // Validación final
                if (!this.isFormValid) {
                    this.showError('Formulario inválido', 'Por favor corrige los errores antes de continuar');
                    return;
                }
                
                this.submitting = true;
                
                try {
                    // Confirmar antes de crear
                    const confirmed = await this.showConfirmation(
                        '¿Crear nueva versión?',
                        `Se creará la versión ${this.form.version}${this.form.isLatest ? ' y se establecerá como actual' : ''}.`,
                        'Sí, crear'
                    );
                    
                    if (!confirmed) {
                        this.submitting = false;
                        return;
                    }
                    
                    // Preparar datos
                    const formData = new FormData();
                    formData.append('version', this.form.version);
                    formData.append('release_notes', this.form.releaseNotes);
                    if (this.form.isLatest) {
                        formData.append('is_latest', 'on');
                    }
                    
                    console.log('Enviando datos:', {
                        version: this.form.version,
                        release_notes: this.form.releaseNotes,
                        is_latest: this.form.isLatest
                    });
                    
                    // Enviar petición
                    const response = await axios.post(window.location.href, formData, {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    });
                    
                    if (response.status === 200) {
                        this.showSuccess(
                            '¡Versión creada!', 
                            `La versión ${this.form.version} ha sido creada exitosamente`
                        );
                        
                        // Emitir evento SocketIO si está conectado
                        if (this.isSocketConnected) {
                            this.emitSocket('version_created', {
                                version: this.form.version,
                                is_latest: this.form.isLatest
                            });
                        }
                        
                        // Redirigir después de un momento
                        setTimeout(() => {
                            window.location.href = '/admin/versions';
                        }, 1500);
                    }
                    
                } catch (error) {
                    console.error('Error creando versión:', error);
                    
                    let errorMessage = 'Error inesperado al crear la versión';
                    
                    if (error.response) {
                        // Error del servidor
                        switch (error.response.status) {
                            case 400:
                                errorMessage = 'Datos del formulario inválidos';
                                break;
                            case 409:
                                errorMessage = 'Esta versión ya existe';
                                break;
                            case 422:
                                errorMessage = error.response.data?.message || 'Datos inválidos';
                                break;
                            default:
                                errorMessage = error.response.data?.message || 'Error del servidor';
                        }
                    } else if (error.request) {
                        errorMessage = 'No se pudo conectar con el servidor';
                    }
                    
                    this.showError('Error al crear versión', errorMessage);
                    
                } finally {
                    this.submitting = false;
                }
            },
            
            /**
             * Resetear formulario
             */
            resetForm() {
                this.form = {
                    version: '',
                    isLatest: true,
                    releaseNotes: ''
                };
                this.versionError = '';
                this.updatePreview();
            },
            
            /**
             * Manejar notificaciones desde SocketIO
             */
            handleSocketNotification(data) {
                // Llamar al método padre
                SocketMixin.methods.handleSocketNotification.call(this, data);
                
                // Manejar notificaciones específicas si es necesario
                if (data.data && data.data.action === 'version_conflict') {
                    this.showWarning(
                        'Conflicto de versión', 
                        'Otra versión fue creada mientras editabas. Verifica los datos.'
                    );
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
             * Observar cambios en el campo versión para validación en tiempo real
             */
            'form.version'(newValue) {
                // Debounce para evitar validación excesiva
                clearTimeout(this.validationTimeout);
                this.validationTimeout = setTimeout(() => {
                    this.updatePreview();
                }, 300);
            },
            
            /**
             * Observar cambios en isLatest
             */
            'form.isLatest'() {
                this.updatePreview();
            },
            
            /**
             * Observar cambios en notas
             */
            'form.releaseNotes'() {
                this.updatePreview();
            }
        }
    });
    
    // Exponer para debugging en desarrollo
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.createVersionApp = createVersionApp;
        console.log('✅ Create Version app disponible en window.createVersionApp para debugging');
    }
    
    console.log('✅ Create Version Vue.js inicializado exitosamente');
});