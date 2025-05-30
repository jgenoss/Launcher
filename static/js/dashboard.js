/**
 * dashboard.js - Lógica Vue.js para el Dashboard
 * Separado completamente del template Jinja2
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
    
    // Verificar que los datos del servidor estén disponibles
    if (typeof window.DASHBOARD_DATA === 'undefined') {
        console.error('❌ DASHBOARD_DATA no está disponible');
        window.DASHBOARD_DATA = {
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
            chartData: []
        };
    } else {
        console.log('✅ DASHBOARD_DATA disponible:', window.DASHBOARD_DATA);
    }
    
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
                // Estados reactivos inicializados con datos del servidor
                stats: {
                    totalVersions: window.DASHBOARD_DATA.stats.totalVersions || 0,
                    totalFiles: window.DASHBOARD_DATA.stats.totalFiles || 0,
                    totalUpdates: window.DASHBOARD_DATA.stats.totalUpdates || 0,
                    totalDownloads: window.DASHBOARD_DATA.stats.totalDownloads || 0,
                    recentDownloads: window.DASHBOARD_DATA.stats.recentDownloads || 0,
                    activeMessages: window.DASHBOARD_DATA.stats.activeMessages || 0,
                    latestVersion: window.DASHBOARD_DATA.stats.latestVersion || ''
                },
                systemStatus: {
                    gameVersion: window.DASHBOARD_DATA.systemStatus.gameVersion || '',
                    launcherVersion: window.DASHBOARD_DATA.systemStatus.launcherVersion || ''
                },
                apiStatus: {
                    online: true
                },
                recentActivity: {
                    downloadsByType: [],
                    error: false
                },
                loadingActivity: false,
                loading: false,
                loadingMessage: 'Cargando...',
                chart: null,
                autoRefreshInterval: null,
                isSocketConnected: false,
                socket: null,
                // Datos del gráfico desde el servidor
                chartData: window.DASHBOARD_DATA.chartData || []
            };
        },

    
        mounted() {
            console.log('Vue mounted - Dashboard inicializado');
            console.log('Stats iniciales:', this.stats);
            console.log('System status inicial:', this.systemStatus);
            
            // Inicializar SocketIO
            this.initSocket();
            
            // Esperar un poco para que el DOM esté completamente renderizado
            this.$nextTick(() => {
                this.initializeChart();
                this.checkApiStatus();
                this.loadRecentActivity();
            });
            
            // Auto-refresh cada 30 segundos
            this.autoRefreshInterval = setInterval(() => {
                this.checkApiStatus();
            }, 30000);
        },

    beforeDestroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        if (this.chart) {
            this.chart.destroy();
        }
    },

    methods: {
        /**
         * Inicializar gráfico de descargas con Chart.js
         */
        initializeChart() {
            const ctx = document.getElementById('downloadsChart');
            if (!ctx) {
                console.warn('Canvas downloadsChart no encontrado - el gráfico se inicializará cuando esté disponible');
                return;
            }

            const chartData = this.chartData;
            console.log('Inicializando gráfico con datos:', chartData);

            // Verificar que tengamos datos para el gráfico
            if (!chartData || chartData.length === 0) {
                console.warn('No hay datos para el gráfico');
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
                                stepSize: 1
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
                const data = await this.apiGet('/api/status');
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
                const data = await this.apiGet('/api/stats');
                
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
            this.setLoading(true, 'Actualizando estadísticas...');
            
            try {
                // Cargar estadísticas del servidor
                const statsData = await this.apiGet('/api/stats');
                
                // Actualizar estadísticas locales
                if (statsData) {
                    this.stats = {
                        ...this.stats,
                        totalDownloads: statsData.total_downloads || this.stats.totalDownloads,
                        activeMessages: statsData.active_messages || this.stats.activeMessages
                    };
                }
                
                // Verificar API y cargar actividad
                await Promise.all([
                    this.checkApiStatus(),
                    this.loadRecentActivity()
                ]);
                
                this.showSuccess('Actualizado', 'Estadísticas actualizadas correctamente');
                console.log('Estadísticas refrescadas manualmente');
            } catch (error) {
                this.showError('Error', 'No se pudieron actualizar las estadísticas');
                console.error('Error refreshing stats:', error);
            } finally {
                this.setLoading(false);
            }
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
            
            // Manejar notificaciones específicas del dashboard
            if (data.data && data.data.action) {
                switch (data.data.action) {
                    case 'version_created':
                        this.stats.totalVersions++;
                        if (data.data.is_latest) {
                            this.systemStatus.gameVersion = data.data.version;
                            this.stats.latestVersion = data.data.version;
                        }
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
                const response = await this.apiGet('/admin/dashboard-chart-data');
                if (response && response.downloads_by_day) {
                    this.chartData = response.downloads_by_day;
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