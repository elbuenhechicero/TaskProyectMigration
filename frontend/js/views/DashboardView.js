/**
 * DashboardView - Vista principal del dashboard
 * Muestra estadísticas, tareas recientes y navegación
 */
class DashboardView extends BaseView {
    constructor(taskService, projectService, authService) {
        super('pageContent');
        this.taskService = taskService;
        this.projectService = projectService;
        this.authService = authService;
        this.stats = null;
    }

    /**
     * Renderizar el dashboard
     */
    async render() {
        if (!this.container) {
            console.error('Dashboard container not found');
            return;
        }

        // Mostrar loading mientras se cargan los datos
        this.container.innerHTML = this.getLoadingTemplate();

        try {
            // Cargar datos del dashboard
            await this.loadDashboardData();
            
            // Renderizar contenido completo
            this.container.innerHTML = this.getDashboardTemplate();
            
            // Configurar eventos y componentes interactivos
            this.setupEventListeners();
            this.renderCharts();
            
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.container.innerHTML = this.getErrorTemplate(error.message);
        }
    }

    /**
     * Cargar datos necesarios para el dashboard
     */
    async loadDashboardData() {
        try {
            const [tasks, projects] = await Promise.all([
                this.taskService.getAllTasks(),
                this.projectService.getAllProjects()
            ]);

            this.tasks = tasks;
            this.projects = projects;
            this.stats = await this.calculateStats();

        } catch (error) {
            console.warn('Some dashboard data could not be loaded:', error);
            // Usar datos mock como fallback
            this.tasks = [];
            this.projects = [];
            this.stats = this.getMockStats();
        }
    }

    /**
     * Calcular estadísticas del dashboard
     */
    async calculateStats() {
        const taskStats = await this.taskService.getTaskStats();
        
        return {
            totalTasks: this.tasks.length,
            completedTasks: this.tasks.filter(t => t.completed).length,
            pendingTasks: this.tasks.filter(t => t.status === 'Pendiente').length,
            overdueTasks: this.tasks.filter(t => t.isOverdue()).length,
            totalProjects: this.projects.length,
            activeProjects: this.projects.filter(p => p.status === 'Activo').length,
            completedProjects: this.projects.filter(p => p.status === 'Completado').length,
            recentTasks: this.tasks.slice(0, 5),
            urgentTasks: this.tasks.filter(t => t.priority === 'Crítica' || t.isOverdue()).slice(0, 3)
        };
    }

    /**
     * Template de loading
     */
    getLoadingTemplate() {
        return `
            <div class="animate-pulse">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    ${Array(4).fill(0).map(() => `
                        <div class="card">
                            <div class="card-body">
                                <div class="h-4 bg-gray-200 rounded mb-2"></div>
                                <div class="h-8 bg-gray-200 rounded mb-2"></div>
                                <div class="h-3 bg-gray-200 rounded"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="card">
                        <div class="card-header">
                            <div class="h-5 bg-gray-200 rounded w-32"></div>
                        </div>
                        <div class="card-body">
                            <div class="space-y-3">
                                ${Array(5).fill(0).map(() => `
                                    <div class="h-4 bg-gray-200 rounded"></div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header">
                            <div class="h-5 bg-gray-200 rounded w-32"></div>
                        </div>
                        <div class="card-body">
                            <div class="h-64 bg-gray-200 rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Template principal del dashboard
     */
    getDashboardTemplate() {
        const currentUser = this.authService.getCurrentUser();
        
        return `
            <div class="dashboard-container fade-in">
                <!-- Header de bienvenida -->
                <div class="mb-8">
                    <h1 class="text-3xl font-bold text-gray-900 mb-2">
                        ¡Bienvenido, ${currentUser ? currentUser.getFullName() : 'Usuario'}!
                    </h1>
                    <p class="text-gray-600">
                        Aquí tienes un resumen de tus proyectos y tareas.
                        <span class="text-sm text-gray-500 ml-2">
                            ${this.formatDate(new Date().toISOString())}
                        </span>
                    </p>
                </div>

                <!-- Tarjetas de estadísticas -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    ${this.getStatsCards()}
                </div>

                <!-- Contenido principal en dos columnas -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <!-- Tareas recientes -->
                    <div class="card">
                        <div class="card-header flex items-center justify-between">
                            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                                <i class="fas fa-tasks mr-2 text-blue-600"></i>
                                Tareas Recientes
                            </h2>
                            <button id="viewAllTasks" class="text-sm text-blue-600 hover:text-blue-800 font-medium">
                                Ver todas <i class="fas fa-arrow-right ml-1"></i>
                            </button>
                        </div>
                        <div class="card-body">
                            ${this.getRecentTasksTemplate()}
                        </div>
                    </div>

                    <!-- Gráfico de progreso de proyectos -->
                    <div class="card">
                        <div class="card-header">
                            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                                <i class="fas fa-chart-pie mr-2 text-green-600"></i>
                                Estado de Proyectos
                            </h2>
                        </div>
                        <div class="card-body">
                            <div id="projectsChart" class="h-64 flex items-center justify-center">
                                ${this.getProjectsChartTemplate()}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sección de tareas urgentes y acciones rápidas -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Tareas urgentes -->
                    <div class="lg:col-span-2">
                        <div class="card">
                            <div class="card-header">
                                <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                                    <i class="fas fa-exclamation-triangle mr-2 text-red-600"></i>
                                    Tareas Urgentes
                                </h2>
                            </div>
                            <div class="card-body">
                                ${this.getUrgentTasksTemplate()}
                            </div>
                        </div>
                    </div>

                    <!-- Acciones rápidas -->
                    <div class="card">
                        <div class="card-header">
                            <h2 class="text-lg font-semibold text-gray-900 flex items-center">
                                <i class="fas fa-bolt mr-2 text-yellow-600"></i>
                                Acciones Rápidas
                            </h2>
                        </div>
                        <div class="card-body">
                            ${this.getQuickActionsTemplate()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generar tarjetas de estadísticas
     */
    getStatsCards() {
        const cards = [
            {
                title: 'Total Tareas',
                value: this.stats.totalTasks,
                icon: 'fas fa-tasks',
                color: 'blue',
                subtitle: `${this.stats.completedTasks} completadas`
            },
            {
                title: 'Tareas Pendientes',
                value: this.stats.pendingTasks,
                icon: 'fas fa-clock',
                color: 'yellow',
                subtitle: `${this.stats.overdueTasks} vencidas`
            },
            {
                title: 'Proyectos Activos',
                value: this.stats.activeProjects,
                icon: 'fas fa-project-diagram',
                color: 'green',
                subtitle: `${this.stats.totalProjects} total`
            },
            {
                title: 'Progreso General',
                value: `${Math.round((this.stats.completedTasks / Math.max(this.stats.totalTasks, 1)) * 100)}%`,
                icon: 'fas fa-chart-line',
                color: 'purple',
                subtitle: 'Tareas completadas'
            }
        ];

        return cards.map(card => `
            <div class="card card-hover">
                <div class="card-body">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-sm font-medium text-gray-600">${card.title}</p>
                            <p class="text-3xl font-bold text-${card.color}-600">${card.value}</p>
                            <p class="text-xs text-gray-500 mt-1">${card.subtitle}</p>
                        </div>
                        <div class="p-3 bg-${card.color}-100 rounded-full">
                            <i class="${card.icon} text-${card.color}-600 text-xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Template de tareas recientes
     */
    getRecentTasksTemplate() {
        if (!this.stats.recentTasks || this.stats.recentTasks.length === 0) {
            return `
                <div class="text-center py-8 text-gray-500">
                    <i class="fas fa-inbox text-4xl mb-4"></i>
                    <p class="text-lg">No hay tareas recientes</p>
                    <button id="createFirstTask" class="mt-4 btn btn-primary">
                        Crear primera tarea
                    </button>
                </div>
            `;
        }

        return `
            <div class="space-y-3">
                ${this.stats.recentTasks.map(task => `
                    <div class="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer task-item ${task.getPriorityClass()}" data-task-id="${task.id}">
                        <div class="flex-shrink-0 mr-3">
                            <div class="w-8 h-8 rounded-full bg-${task.completed ? 'green' : 'blue'}-100 flex items-center justify-center">
                                <i class="fas fa-${task.completed ? 'check' : 'circle'} text-${task.completed ? 'green' : 'blue'}-600"></i>
                            </div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-medium text-gray-900 ${task.completed ? 'line-through' : ''}">
                                ${this.escapeHtml(task.title)}
                            </p>
                            <p class="text-xs text-gray-500 truncate">
                                ${task.dueDate ? 'Vence: ' + this.formatDate(task.dueDate) : 'Sin fecha límite'}
                            </p>
                        </div>
                        <div class="flex-shrink-0">
                            <span class="inline-flex items-center px-2 py-1 text-xs font-medium rounded tag-${task.priority.toLowerCase()}">
                                ${task.priority}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Template del gráfico de proyectos
     */
    getProjectsChartTemplate() {
        const projectsByStatus = {};
        Project.VALID_STATUSES.forEach(status => {
            projectsByStatus[status] = this.projects.filter(p => p.status === status).length;
        });

        return `
            <div class="w-full">
                ${Object.entries(projectsByStatus).map(([status, count]) => {
                    const percentage = this.stats.totalProjects > 0 ? (count / this.stats.totalProjects) * 100 : 0;
                    const statusInfo = new Project().getStatusInfo();
                    const info = statusInfo;
                    
                    return `
                        <div class="flex items-center justify-between mb-3">
                            <div class="flex items-center">
                                <div class="w-3 h-3 rounded-full mr-2" style="background-color: ${info.color || '#6B7280'}"></div>
                                <span class="text-sm text-gray-700">${status}</span>
                            </div>
                            <div class="flex items-center">
                                <div class="w-24 bg-gray-200 rounded-full h-2 mr-2">
                                    <div class="h-2 rounded-full transition-all duration-300" 
                                         style="width: ${percentage}%; background-color: ${info.color || '#6B7280'}">
                                    </div>
                                </div>
                                <span class="text-sm font-medium text-gray-900 w-8">${count}</span>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    /**
     * Template de tareas urgentes
     */
    getUrgentTasksTemplate() {
        if (!this.stats.urgentTasks || this.stats.urgentTasks.length === 0) {
            return `
                <div class="text-center py-6 text-gray-500">
                    <i class="fas fa-check-circle text-3xl mb-2 text-green-500"></i>
                    <p>¡Excelente! No hay tareas urgentes.</p>
                </div>
            `;
        }

        return `
            <div class="space-y-3">
                ${this.stats.urgentTasks.map(task => `
                    <div class="border-l-4 border-red-400 bg-red-50 p-3 rounded-r cursor-pointer task-item" data-task-id="${task.id}">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <h4 class="font-medium text-red-900">${this.escapeHtml(task.title)}</h4>
                                <p class="text-sm text-red-700 mt-1">
                                    ${task.isOverdue() ? '🔥 Vencida' : '⚠️ Crítica'} 
                                    ${task.dueDate ? '- Vence: ' + this.formatRelativeDate(task.dueDate) : ''}
                                </p>
                            </div>
                            <button class="text-red-600 hover:text-red-800 complete-task" data-task-id="${task.id}">
                                <i class="fas fa-check-circle text-lg"></i>
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Template de acciones rápidas
     */
    getQuickActionsTemplate() {
        return `
            <div class="space-y-3">
                <button class="w-full btn btn-primary text-left justify-start" id="quickCreateTask">
                    <i class="fas fa-plus mr-3"></i>
                    Crear nueva tarea
                </button>
                <button class="w-full btn btn-secondary text-left justify-start" id="quickCreateProject">
                    <i class="fas fa-folder-plus mr-3"></i>
                    Nuevo proyecto
                </button>
                <button class="w-full btn btn-outline text-left justify-start" id="viewReports">
                    <i class="fas fa-chart-bar mr-3"></i>
                    Ver reportes
                </button>
                <button class="w-full btn btn-outline text-left justify-start" id="viewCalendar">
                    <i class="fas fa-calendar-alt mr-3"></i>
                    Calendario
                </button>
            </div>
        `;
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Navegación
        const viewAllTasksBtn = this.container.querySelector('#viewAllTasks');
        if (viewAllTasksBtn) {
            viewAllTasksBtn.onclick = () => {
                document.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'tasks' } }));
            };
        }

        // Acciones rápidas
        const quickCreateTask = this.container.querySelector('#quickCreateTask');
        if (quickCreateTask) {
            quickCreateTask.onclick = () => this.showQuickTaskModal();
        }

        const quickCreateProject = this.container.querySelector('#quickCreateProject');
        if (quickCreateProject) {
            quickCreateProject.onclick = () => {
                document.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'projects', data: { action: 'create' } } }));
            };
        }

        // Clicks en tareas
        const taskItems = this.container.querySelectorAll('.task-item');
        taskItems.forEach(item => {
            item.onclick = (e) => {
                if (!e.target.classList.contains('complete-task')) {
                    const taskId = parseInt(item.dataset.taskId);
                    this.showTaskDetails(taskId);
                }
            };
        });

        // Completar tareas urgentes
        const completeButtons = this.container.querySelectorAll('.complete-task');
        completeButtons.forEach(btn => {
            btn.onclick = async (e) => {
                e.stopPropagation();
                const taskId = parseInt(btn.dataset.taskId);
                await this.completeTask(taskId);
            };
        });
    }

    /**
     * Mostrar modal rápido para crear tarea
     */
    showQuickTaskModal() {
        // TODO: Implementar modal de creación rápida
        console.log('Quick task modal not implemented yet');
        // Por ahora, navegar a la vista completa de tareas
        document.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'tasks', data: { action: 'create' } } }));
    }

    /**
     * Mostrar detalles de tarea
     */
    showTaskDetails(taskId) {
        // TODO: Implementar modal de detalles de tarea
        console.log(`Show task details for task ${taskId}`);
        document.dispatchEvent(new CustomEvent('navigate', { detail: { view: 'tasks', data: { taskId } } }));
    }

    /**
     * Completar tarea
     */
    async completeTask(taskId) {
        try {
            await this.taskService.completeTask(taskId);
            // Recargar estadísticas y actualizar vista
            await this.loadDashboardData();
            this.render();
            
            // Mostrar notificación de éxito
            this.showSuccess('¡Tarea completada exitosamente!');
            
        } catch (error) {
            console.error('Error completing task:', error);
            this.showError(error.message || 'Error al completar la tarea');
        }
    }

    /**
     * Renderizar gráficos (placeholder para futuras mejoras)
     */
    renderCharts() {
        // TODO: Integrar librería de gráficos como Chart.js o similar
        console.log('Charts rendering not implemented yet');
    }

    /**
     * Datos mock para desarrollo
     */
    getMockStats() {
        return {
            totalTasks: 15,
            completedTasks: 8,
            pendingTasks: 5,
            overdueTasks: 2,
            totalProjects: 3,
            activeProjects: 2,
            completedProjects: 1,
            recentTasks: [],
            urgentTasks: []
        };
    }

    /**
     * Template de error
     */
    getErrorTemplate(message) {
        return `
            <div class="text-center py-12">
                <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                <h2 class="text-xl font-bold text-gray-900 mb-2">Error al cargar el dashboard</h2>
                <p class="text-gray-600 mb-4">${message}</p>
                <button onclick="location.reload()" class="btn btn-primary">
                    <i class="fas fa-redo mr-2"></i>Reintentar
                </button>
            </div>
        `;
    }
}