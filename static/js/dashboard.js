/**
 * dashboard.js - Lógica Vue.js para el Dashboard
 * Ahora carga todos los datos vía API.
 */

// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOMContentLoaded - Iniciando Dashboard Vue.js');
    
    // Verificar que Vue esté disponible
    if (typeof Vue === 'undefined') {
        console.error('❌ Vue.js no está disponible');
        return;
    }
    console.log('✅ Vue.js disponible');
    
    // Verificar que el elemento #app existe
    const appElement = document.getElementById('app');
    if (!appElement) {
        console.error('❌ Elemento #app no encontrado en el DOM');
        return;
    }
    console.log('✅ Elemento #app encontrado');
    
    // Verificar que los mixins estén disponibles
    if (typeof NotificationMixin === 'undefined') {
        console.error('❌ NotificationMixin no está disponible');
        return;
    }
    console.log('✅ Mixins disponibles');

    // Configurar delimitadores de Vue ANTES de crear la instancia
    Vue.config.delimiters = ['[[', ']]'];
    console.log('✅ Delimitadores Vue configurados: [[, ]]');
    
    console.log('🔧 Creando instancia Vue...');

    // Crear instancia Vue para el Dashboard
    const dashboardApp = new Vue({
        el: '#app',
        delimiters: ['[[', ']]'], // Configurar delimitadores específicamente para esta instancia
        mixins: [NotificationMixin, HttpMixin, UtilsMixin, SocketMixin],
        data() {
            return {
                // Estados reactivos inicializados con valores por defecto
                stats: {
                    totalVersions: 0,
                    totalFiles: 0,
                    totalUpdates: 0,
                    totalDownloads: 0,
                    recentDownloads: 0,
                    activeMessages: 0,
                    latestVersion: ''
                },
                systemStatus: {
                    gameVersion: '',
                    launcherVersion: ''
                },
                apiStatus: {
                    online: true
                },
                recentActivity: {
                    downloadsByType: [],
                    error: false
                },
                loadingActivity: false,
                loading: false, // Controla el overlay de carga global
                loadingMessage: 'Cargando...',
                chart: null,
                autoRefreshInterval: null,
                isSocketConnected: false, // Gestionado por SocketMixin
                socket: null, // Gestionado por SocketMixin
                chartData: [] // Los datos del gráfico se cargarán vía API
            };
        },

    
        mounted() {
            console.log('Vue mounted - Dashboard inicializado');
            
            // Inicializar SocketIO
            this.initSocket();
            
            // Cargar todos los datos del dashboard después de que Vue esté montado
            this.loadDashboardData();
            
            // Cargar actividad reciente y estado de API periódicamente
            this.autoRefreshInterval = setInterval(() => {
                this.checkApiStatus(); // Puede ser cada 30 segundos
                this.loadRecentActivity(); // Y esto también puede ser menos frecuente o activado por socket
            }, 30000); // Ejemplo: Refrescar cada 30 segundos

            // Refrescar el gráfico de descargas cada 5 minutos
            this.chartRefreshInterval = setInterval(() => {
                this.refreshChartData();
            }, 300000); // 5 minutos
        },

    beforeDestroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        if (this.chartRefreshInterval) { // Limpiar el nuevo intervalo
            clearInterval(this.chartRefreshInterval);
        }
        if (this.chart) {
            this.chart.destroy();
        }
    },

    methods: {
        /**
         * Cargar todos los datos del dashboard desde la API
         */
        async loadDashboardData() {
            this.setLoading(true, 'Cargando datos del dashboard...');
            try {
                const data = await this.apiGet('/admin/api/dashboard_data');
                
                // Actualizar todas las propiedades de datos
                this.stats.totalVersions = data.stats.totalVersions;
                this.stats.totalFiles = data.stats.totalFiles;
                this.stats.totalUpdates = data.stats.totalUpdates;
                this.stats.totalDownloads = data.stats.totalDownloads;
                this.stats.recentDownloads = data.stats.recentDownloads;
                this.stats.activeMessages = data.stats.activeMessages;
                this.stats.latestVersion = data.stats.latestVersion;

                this.systemStatus.gameVersion = data.systemStatus.gameVersion;
                this.systemStatus.launcherVersion = data.systemStatus.launcherVersion;
                
                this.chartData = data.chartData; // Asignar datos del gráfico
                this.initializeChart(); // Inicializar el gráfico con los datos cargados

                await this.loadRecentActivity(); // Cargar actividad reciente por separado
                await this.checkApiStatus(); // Verificar estado de la API

                console.log('✅ Datos del dashboard cargados:', this.stats, this.systemStatus);
            } catch (error) {
                this.showError('Error', 'No se pudieron cargar los datos del dashboard');
                console.error('Error loading dashboard data:', error);
            } finally {
                this.setLoading(false);
            }
        },

        /**
         * Inicializar gráfico de descargas con Chart.js
         */
        initializeChart() {
            const ctx = document.getElementById('downloadsChart');
            if (!ctx) {
                console.warn('Canvas downloadsChart no encontrado - el gráfico se inicializará cuando esté disponible');
                return;
            }

            // Destruir instancia anterior si existe
            if (this.chart) {
                this.chart.destroy();
            }

            const chartData = this.chartData;
            console.log('Inicializando gráfico con datos:', chartData);

            // Verificar que tengamos datos para el gráfico
            if (!chartData || chartData.length === 0) {
                console.warn('No hay datos para el gráfico. Mostrando gráfico vacío.');
                // Puedes optar por mostrar un mensaje en el canvas o dejarlo vacío
                this.chart = new Chart(ctx, { /* ... config básica para canvas vacío ... */ });
                return;
            }

            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map(d => {
                        const date = new Date(d.date);
                        return date.toLocaleDateString('es-ES', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric'
                        });
                    }),
                    datasets: [{
                        label: 'Descargas',
                        data: chartData.map(d => d.count),
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1 // Asegura pasos enteros si solo hay descargas unitarias
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 4,
                            hoverRadius: 6
                        }
                    }
                }
            });
        },

        /**
         * Verificar estado de la API
         */
        async checkApiStatus() {
            try {
                const data = await this.apiGet('/api/status'); // Esta API ya existe y es de solo datos
                this.apiStatus.online = data.status === 'online';
                
                // Actualizar estadísticas del sistema si están disponibles
                if (data.latest_game_version) {
                    this.systemStatus.gameVersion = data.latest_game_version;
                }
                if (data.current_launcher_version) {
                    this.systemStatus.launcherVersion = data.current_launcher_version;
                }
                
                console.log('API Status verificado:', this.apiStatus.online);
            } catch (error) {
                this.apiStatus.online = false;
                console.error('Error checking API status:', error);
            }
        },

        /**
         * Cargar actividad reciente desde la API
         */
        async loadRecentActivity() {
            this.loadingActivity = true;
            this.recentActivity.error = false;
            
            try {
                const data = await this.apiGet('/api/stats'); // Esta API ya existe y es de solo datos
                
                // Procesar datos de descargas por tipo
                this.recentActivity.downloadsByType = [];
                if (data.downloads_by_type) {
                    for (const [type, count] of Object.entries(data.downloads_by_type)) {
                        this.recentActivity.downloadsByType.push({
                            type: type,
                            count: count
                        });
                    }
                }
                
                console.log('Actividad reciente cargada:', this.recentActivity.downloadsByType);
            } catch (error) {
                this.recentActivity.error = true;
                console.error('Error loading recent activity:', error);
            } finally {
                this.loadingActivity = false;
            }
        },

        /**
         * Refrescar todas las estadísticas manualmente
         */
        async refreshStats() {
            // Un solo punto de entrada para recargar todo
            await this.loadDashboardData();
            this.showSuccess('Actualizado', 'Estadísticas actualizadas correctamente');
            console.log('Estadísticas refrescadas manualmente');
        },

        /**
         * Sobrescribir manejo de actualización de estadísticas desde SocketIO
         * @param {Object} data - Datos de estadísticas desde SocketIO
         */
        handleStatsUpdate(data) {
            console.log('Stats update from SocketIO:', data);
            
            // Actualizar estadísticas en tiempo real
            if (data.total_downloads !== undefined) {
                this.stats.totalDownloads = data.total_downloads;
            }
            if (data.total_versions !== undefined) {
                this.stats.totalVersions = data.total_versions;
            }
            if (data.total_files !== undefined) {
                this.stats.totalFiles = data.total_files;
            }
            if (data.total_updates !== undefined) {
                this.stats.totalUpdates = data.total_updates;
            }
            if (data.active_messages !== undefined) {
                this.stats.activeMessages = data.active_messages;
            }
            if (data.latest_version) {
                this.stats.latestVersion = data.latest_version;
                this.systemStatus.gameVersion = data.latest_version;
            }
            
            // Aquí, en lugar de llamar a refreshChartData, si el socket enviara los datos del gráfico
            // también se actualizaría directamente, pero por ahora se mantiene la llamada API periódica.
            
            // Mostrar notificación de actualización en tiempo real
            this.showInfo('Actualización automática', 'Estadísticas actualizadas en tiempo real');
        },

        /**
         * Manejar notificaciones específicas del dashboard desde SocketIO
         * @param {Object} data - Datos de notificación
         */
        handleSocketNotification(data) {
            // Llamar al método padre para manejo general
            SocketMixin.methods.handleSocketNotification.call(this, data);
            
            // Manejar notificaciones específicas del dashboard para actualizar contadores
            if (data.data && data.data.action) {
                switch (data.data.action) {
                    case 'version_created':
                        this.stats.totalVersions++;
                        if (data.data.is_latest) {
                            this.systemStatus.gameVersion = data.data.version;
                            this.stats.latestVersion = data.data.version;
                        }
                        // Forzar una actualización del gráfico si se crea una versión (puede afectar descargas)
                        this.refreshChartData(); 
                        break;
                        
                    case 'files_uploaded':
                        this.stats.totalFiles += data.data.count || 1;
                        break;
                        
                    case 'update_created':
                        this.stats.totalUpdates++;
                        break;
                        
                    case 'message_created':
                        if (data.data.is_active) {
                            this.stats.activeMessages++;
                        }
                        break;
                        
                    case 'launcher_uploaded':
                        if (data.data.is_current) {
                            this.systemStatus.launcherVersion = data.data.version;
                        }
                        break;
                }
            }
        },

        /**
         * Actualizar gráfico con nuevos datos
         * @param {Array} newChartData - Nuevos datos para el gráfico
         */
        updateChart(newChartData) {
            if (!this.chart || !newChartData) return;
            
            this.chart.data.labels = newChartData.map(d => {
                const date = new Date(d.date);
                return date.toLocaleDateString('es-ES', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric'
                });
            });
            
            this.chart.data.datasets[0].data = newChartData.map(d => d.count);
            this.chart.update();
            
            console.log('Gráfico actualizado con nuevos datos');
        },

        /**
         * Obtener datos frescos del gráfico desde el servidor
         */
        async refreshChartData() {
            try {
                // Se podría crear una API específica para solo datos del gráfico si los datos son pesados.
                // Por ahora, se reutiliza get_dashboard_data.
                const response = await this.apiGet('/admin/api/dashboard_data');
                if (response && response.chartData) {
                    this.chartData = response.chartData;
                    this.updateChart(this.chartData);
                }
            } catch (error) {
                console.error('Error refreshing chart data:', error);
            }
        },

        /**
         * Establecer estado de carga global
         * @param {Boolean} isLoading - Estado de carga
         * @param {String} message - Mensaje de carga
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

    /**
     * Observadores para cambios de estado
     */
    watch: {
        // Observar cambios en el estado de conexión de la API
        'apiStatus.online'(newValue, oldValue) {
            if (newValue !== oldValue) {
                const status = newValue ? 'conectado' : 'desconectado';
                console.log(`API ${status}`);
                
                if (!newValue) {
                    this.showWarning('API Desconectada', 'La conexión con la API se ha perdido');
                } else if (oldValue === false) {
                    this.showSuccess('API Conectada', 'La conexión con la API se ha restablecido');
                }
            }
        },

        // Observar cambios en estadísticas críticas
        'stats.totalDownloads'(newValue, oldValue) {
            if (oldValue > 0 && newValue > oldValue) {
                console.log(`Nuevas descargas: ${newValue - oldValue}`);
            }
        }
    }
    });
    console.log('✅ Instancia Vue creada:', dashboardApp);

    // Exponer la instancia para debugging (solo en desarrollo)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.dashboardApp = dashboardApp;
        console.log('Dashboard app disponible en window.dashboardApp para debugging');
    }

    console.log('Dashboard.js inicializado exitosamente');
});