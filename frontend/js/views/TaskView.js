/**
 * TaskView - Vista para gestión de tareas
 */
class TaskView extends BaseView {
    constructor(taskService, projectService) {
        super('pageContent');
        this.taskService = taskService;
        this.projectService = projectService;
        this.tasks = [];
        this.projects = [];
        this.filters = {
            status: 'all',
            priority: 'all',
            projectId: 'all',
            search: ''
        };
    }

    /**
     * Renderizar vista de tareas
     */
    async render(options = {}) {
        if (!this.container) {
            console.error('Task container not found');
            return;
        }

        this.container.innerHTML = this.getLoadingTemplate();

        try {
            await this.loadTasksData();
            this.container.innerHTML = this.getTasksTemplate();
            this.setupEventListeners();
            this.applyFilters();

        } catch (error) {
            console.error('Error loading tasks:', error);
            this.showError('Error al cargar las tareas');
        }
    }

    /**
     * Cargar datos de tareas y proyectos
     */
    async loadTasksData() {
        try {
            const [tasks, projects] = await Promise.all([
                this.taskService.getAllTasks(),
                this.projectService.getAllProjects()
            ]);

            this.tasks = tasks;
            this.projects = projects;

        } catch (error) {
            console.warn('Could not load from API, using mock data:', error);
            this.tasks = this.taskService.getMockTasks();
            this.projects = this.projectService.getMockProjects();
        }
    }

    /**
     * Template de carga
     */
    getLoadingTemplate() {
        return `
            <div class="animate-pulse">
                <div class="h-10 bg-gray-200 rounded mb-6"></div>
                <div class="space-y-4">
                    ${Array(5).fill(0).map(() => '<div class="h-16 bg-gray-200 rounded"></div>').join('')}
                </div>
            </div>
        `;
    }

    /**
     * Template principal de tareas
     */
    getTasksTemplate() {
        return `
            <div class="tasks-container">
                <!-- Header -->
                <div class="flex items-center justify-between mb-6">
                    <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                        <i class="fas fa-tasks mr-3 text-blue-600"></i>
                        Gestión de Tareas
                    </h1>
                    <button id="createTaskBtn" class="btn btn-primary">
                        <i class="fas fa-plus mr-2"></i>Nueva Tarea
                    </button>
                </div>

                <!-- Filtros y búsqueda -->
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Búsqueda</label>
                            <input type="text" id="searchInput" placeholder="Buscar tareas..." class="form-input">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                            <select id="statusFilter" class="form-select">
                                <option value="all">Todos los estados</option>
                                ${Task.VALID_STATUSES.map(status => `
                                    <option value="${status}">${status}</option>
                                `).join('')}
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Prioridad</label>
                            <select id="priorityFilter" class="form-select">
                                <option value="all">Todas las prioridades</option>
                                ${Task.VALID_PRIORITIES.map(priority => `
                                    <option value="${priority}">${priority}</option>
                                `).join('')}
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Proyecto</label>
                            <select id="projectFilter" class="form-select">
                                <option value="all">Todos los proyectos</option>
                                ${this.projects.map(project => `
                                    <option value="${project.id}">${project.name}</option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Vista de lista de tareas -->
                <div id="tasksContainer" class="space-y-3">
                    ${this.getTasksListTemplate()}
                </div>
            </div>
        `;
    }

    /**
     * Template de lista de tareas
     */
    getTasksListTemplate() {
        if (this.tasks.length === 0) {
            return `
                <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
                    <i class="fas fa-inbox text-5xl text-gray-300 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-600 mb-2">No hay tareas</h3>
                    <p class="text-gray-500 mb-4">Crea una nueva tarea para comenzar</p>
                    <button id="createTaskBtn2" class="btn btn-primary">
                        <i class="fas fa-plus mr-2"></i>Crear tarea
                    </button>
                </div>
            `;
        }

        return this.tasks.map(task => `
            <div class="card task-card cursor-pointer hover:shadow-md transition-all ${task.getPriorityClass()}" data-task-id="${task.id}">
                <div class="card-body flex items-center justify-between">
                    <div class="flex items-center flex-1">
                        <div class="flex-shrink-0">
                            <input type="checkbox" class="w-5 h-5 task-checkbox" ${task.completed ? 'checked' : ''} data-task-id="${task.id}">
                        </div>
                        <div class="ml-4 flex-1">
                            <h3 class="text-lg font-semibold text-gray-900 ${task.completed ? 'line-through text-gray-500' : ''}">
                                ${this.escapeHtml(task.title)}
                            </h3>
                            <p class="text-sm text-gray-600 mt-1 line-clamp-2">
                                ${this.escapeHtml(task.description || 'Sin descripción')}
                            </p>
                            <div class="flex items-center space-x-3 mt-2">
                                ${task.projectId ? `
                                    <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                        ${this.projects.find(p => p.id === task.projectId)?.name || 'Proyecto desconocido'}
                                    </span>
                                ` : ''}
                                ${task.dueDate ? `
                                    <span class="text-xs text-gray-600">
                                        <i class="fas fa-calendar-alt mr-1"></i>
                                        ${this.formatDate(task.dueDate)}
                                    </span>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center space-x-3 ml-4">
                        <span class="px-3 py-1 text-xs font-medium rounded-full ${this.getStatusBadgeColor(task.status)}">
                            ${task.status}
                        </span>
                        <span class="px-3 py-1 text-xs font-medium rounded-full ${this.getPriorityBadgeColor(task.priority)}">
                            ${task.priority}
                        </span>
                        <div class="flex space-x-2">
                            <button class="edit-task-btn text-blue-600 hover:text-blue-800" data-task-id="${task.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="delete-task-btn text-red-600 hover:text-red-800" data-task-id="${task.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Crear tarea
        const createBtns = this.container.querySelectorAll('#createTaskBtn, #createTaskBtn2');
        createBtns.forEach(btn => {
            btn.onclick = () => this.showCreateTaskModal();
        });

        // Filtros
        const searchInput = this.container.querySelector('#searchInput');
        const statusFilter = this.container.querySelector('#statusFilter');
        const priorityFilter = this.container.querySelector('#priorityFilter');
        const projectFilter = this.container.querySelector('#projectFilter');

        [searchInput, statusFilter, priorityFilter, projectFilter].forEach(filter => {
            filter.onchange = () => this.applyFilters();
        });

        // Checkboxes de tareas
        const taskCheckboxes = this.container.querySelectorAll('.task-checkbox');
        taskCheckboxes.forEach(checkbox => {
            checkbox.onchange = async (e) => {
                e.stopPropagation();
                const taskId = parseInt(checkbox.dataset.taskId);
                const task = this.tasks.find(t => t.id === taskId);
                
                if (checkbox.checked && !task.completed) {
                    await this.completeTask(taskId);
                }
            };
        });

        // Editar tarea
        const editBtns = this.container.querySelectorAll('.edit-task-btn');
        editBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const taskId = parseInt(btn.dataset.taskId);
                this.showEditTaskModal(taskId);
            };
        });

        // Eliminar tarea
        const deleteBtns = this.container.querySelectorAll('.delete-task-btn');
        deleteBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const taskId = parseInt(btn.dataset.taskId);
                this.showDeleteConfirmation(taskId);
            };
        });

        // Click en tarjeta de tarea
        const taskCards = this.container.querySelectorAll('.task-card');
        taskCards.forEach(card => {
            card.onclick = (e) => {
                if (!e.target.closest('input, button')) {
                    const taskId = parseInt(card.dataset.taskId);
                    this.showTaskDetails(taskId);
                }
            };
        });
    }

    /**
     * Aplicar filtros a las tareas
     */
    applyFilters() {
        const searchInput = this.container.querySelector('#searchInput');
        const statusFilter = this.container.querySelector('#statusFilter');
        const priorityFilter = this.container.querySelector('#priorityFilter');
        const projectFilter = this.container.querySelector('#projectFilter');

        this.filters = {
            search: searchInput.value.toLowerCase(),
            status: statusFilter.value,
            priority: priorityFilter.value,
            projectId: projectFilter.value
        };

        const filteredTasks = this.tasks.filter(task => {
            // Búsqueda
            if (this.filters.search && !task.title.toLowerCase().includes(this.filters.search) &&
                !task.description.toLowerCase().includes(this.filters.search)) {
                return false;
            }

            // Estado
            if (this.filters.status !== 'all' && task.status !== this.filters.status) {
                return false;
            }

            // Prioridad
            if (this.filters.priority !== 'all' && task.priority !== this.filters.priority) {
                return false;
            }

            // Proyecto
            if (this.filters.projectId !== 'all' && task.projectId !== parseInt(this.filters.projectId)) {
                return false;
            }

            return true;
        });

        // Actualizar vista
        const tasksContainer = this.container.querySelector('#tasksContainer');
        if (filteredTasks.length === 0) {
            tasksContainer.innerHTML = `
                <div class="text-center py-12 bg-white rounded-lg border border-gray-200">
                    <i class="fas fa-search text-5xl text-gray-300 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-600 mb-2">No hay tareas que coincidan</h3>
                    <p class="text-gray-500">Intenta con otros filtros</p>
                </div>
            `;
        } else {
            tasksContainer.innerHTML = filteredTasks.map(task => `
                <div class="card task-card cursor-pointer hover:shadow-md transition-all ${task.getPriorityClass()}" data-task-id="${task.id}">
                    <div class="card-body flex items-center justify-between">
                        <div class="flex items-center flex-1">
                            <div class="flex-shrink-0">
                                <input type="checkbox" class="w-5 h-5 task-checkbox" ${task.completed ? 'checked' : ''} data-task-id="${task.id}">
                            </div>
                            <div class="ml-4 flex-1">
                                <h3 class="text-lg font-semibold text-gray-900 ${task.completed ? 'line-through text-gray-500' : ''}">
                                    ${this.escapeHtml(task.title)}
                                </h3>
                                <p class="text-sm text-gray-600 mt-1 line-clamp-2">
                                    ${this.escapeHtml(task.description || 'Sin descripción')}
                                </p>
                                <div class="flex items-center space-x-3 mt-2">
                                    ${task.projectId ? `
                                        <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                            ${this.projects.find(p => p.id === task.projectId)?.name || 'Proyecto desconocido'}
                                        </span>
                                    ` : ''}
                                    ${task.dueDate ? `
                                        <span class="text-xs text-gray-600">
                                            <i class="fas fa-calendar-alt mr-1"></i>
                                            ${this.formatDate(task.dueDate)}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center space-x-3 ml-4">
                            <span class="px-3 py-1 text-xs font-medium rounded-full ${this.getStatusBadgeColor(task.status)}">
                                ${task.status}
                            </span>
                            <span class="px-3 py-1 text-xs font-medium rounded-full ${this.getPriorityBadgeColor(task.priority)}">
                                ${task.priority}
                            </span>
                            <div class="flex space-x-2">
                                <button class="edit-task-btn text-blue-600 hover:text-blue-800" data-task-id="${task.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="delete-task-btn text-red-600 hover:text-red-800" data-task-id="${task.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            // Re-setup event listeners
            this.setupEventListeners();
        }
    }

    /**
     * Mostrar modal de crear tarea
     */
    showCreateTaskModal() {
        // TODO: Implementar modal de creación
        console.log('Create task modal not implemented yet');
    }

    /**
     * Mostrar modal de editar tarea
     */
    showEditTaskModal(taskId) {
        // TODO: Implementar modal de edición
        console.log('Edit task modal not implemented yet', taskId);
    }

    /**
     * Mostrar detalles de tarea
     */
    showTaskDetails(taskId) {
        // TODO: Implementar vista de detalles
        console.log('Task details modal not implemented yet', taskId);
    }

    /**
     * Completar tarea
     */
    async completeTask(taskId) {
        try {
            await this.taskService.completeTask(taskId);
            const task = this.tasks.find(t => t.id === taskId);
            if (task) {
                task.markAsCompleted();
            }
            this.showSuccess('¡Tarea completada!');
            this.applyFilters();

        } catch (error) {
            console.error('Error completing task:', error);
            this.showError('Error al completar la tarea');
        }
    }

    /**
     * Mostrar confirmación de eliminación
     */
    showDeleteConfirmation(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (!task) return;

        this.showConfirm(
            `¿Está seguro de que desea eliminar la tarea "${task.title}"?`,
            async () => {
                try {
                    await this.taskService.deleteTask(taskId);
                    this.tasks = this.tasks.filter(t => t.id !== taskId);
                    this.showSuccess('Tarea eliminada exitosamente');
                    this.applyFilters();

                } catch (error) {
                    console.error('Error deleting task:', error);
                    this.showError('Error al eliminar la tarea');
                }
            }
        );
    }

    /**
     * Obtener color de badge según estado
     */
    getStatusBadgeColor(status) {
        const colors = {
            'Pendiente': 'bg-gray-100 text-gray-800',
            'En Progreso': 'bg-blue-100 text-blue-800',
            'Completada': 'bg-green-100 text-green-800',
            'Bloqueada': 'bg-orange-100 text-orange-800',
            'Cancelada': 'bg-red-100 text-red-800'
        };
        return colors[status] || colors['Pendiente'];
    }

    /**
     * Obtener color de badge según prioridad
     */
    getPriorityBadgeColor(priority) {
        const colors = {
            'Baja': 'bg-green-100 text-green-800',
            'Media': 'bg-yellow-100 text-yellow-800',
            'Alta': 'bg-orange-100 text-orange-800',
            'Crítica': 'bg-red-100 text-red-800'
        };
        return colors[priority] || colors['Media'];
    }
}