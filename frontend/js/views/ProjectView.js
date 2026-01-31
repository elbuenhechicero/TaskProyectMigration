/**
 * ProjectView - Vista para gestión de proyectos
 */
class ProjectView extends BaseView {
    constructor(projectService, taskService) {
        super('pageContent');
        this.projectService = projectService;
        this.taskService = taskService;
        this.projects = [];
        this.tasks = [];
        this.selectedProjectId = null;
    }

    /**
     * Renderizar vista de proyectos
     */
    async render(selectedProjectId = null) {
        if (!this.container) {
            console.error('Project container not found');
            return;
        }

        this.container.innerHTML = this.getLoadingTemplate();
        this.selectedProjectId = selectedProjectId;

        try {
            await this.loadProjectsData();
            this.container.innerHTML = this.getProjectsTemplate();
            this.setupEventListeners();

        } catch (error) {
            console.error('Error loading projects:', error);
            this.showError('Error al cargar los proyectos');
        }
    }

    /**
     * Cargar datos de proyectos
     */
    async loadProjectsData() {
        try {
            const [projects, tasks] = await Promise.all([
                this.projectService.getAllProjects(),
                this.taskService.getAllTasks()
            ]);

            this.projects = projects;
            this.tasks = tasks;

        } catch (error) {
            console.warn('Could not load from API, using mock data:', error);
            this.projects = this.projectService.getMockProjects();
            this.tasks = this.taskService.getMockTasks();
        }
    }

    /**
     * Template de carga
     */
    getLoadingTemplate() {
        return `
            <div class="animate-pulse">
                <div class="h-10 bg-gray-200 rounded mb-6"></div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${Array(6).fill(0).map(() => '<div class="h-40 bg-gray-200 rounded"></div>').join('')}
                </div>
            </div>
        `;
    }

    /**
     * Template principal de proyectos
     */
    getProjectsTemplate() {
        return `
            <div class="projects-container">
                <!-- Header -->
                <div class="flex items-center justify-between mb-6">
                    <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                        <i class="fas fa-project-diagram mr-3 text-purple-600"></i>
                        Gestión de Proyectos
                    </h1>
                    <button id="createProjectBtn" class="btn btn-primary">
                        <i class="fas fa-plus mr-2"></i>Nuevo Proyecto
                    </button>
                </div>

                <!-- Estadísticas de proyectos -->
                ${this.getProjectStatsTemplate()}

                <!-- Grid de proyectos -->
                <div id="projectsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${this.getProjectsGridTemplate()}
                </div>
            </div>
        `;
    }

    /**
     * Template de estadísticas
     */
    getProjectStatsTemplate() {
        const totalProjects = this.projects.length;
        const activeProjects = this.projects.filter(p => !p.completed).length;
        const completedProjects = this.projects.filter(p => p.completed).length;
        const teamMembers = new Set(this.projects.flatMap(p => p.teamMembers || [])).size;

        return `
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="card">
                    <div class="card-body text-center">
                        <div class="text-4xl font-bold text-blue-600">${totalProjects}</div>
                        <div class="text-gray-600 text-sm">Proyectos Totales</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body text-center">
                        <div class="text-4xl font-bold text-green-600">${completedProjects}</div>
                        <div class="text-gray-600 text-sm">Completados</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body text-center">
                        <div class="text-4xl font-bold text-orange-600">${activeProjects}</div>
                        <div class="text-gray-600 text-sm">En Progreso</div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body text-center">
                        <div class="text-4xl font-bold text-purple-600">${teamMembers}</div>
                        <div class="text-gray-600 text-sm">Miembros del Equipo</div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Template de grid de proyectos
     */
    getProjectsGridTemplate() {
        if (this.projects.length === 0) {
            return `
                <div class="col-span-1 md:col-span-2 lg:col-span-3">
                    <div class="text-center py-16 bg-white rounded-lg border border-gray-200">
                        <i class="fas fa-inbox text-6xl text-gray-300 mb-4"></i>
                        <h3 class="text-2xl font-semibold text-gray-600 mb-2">Sin proyectos</h3>
                        <p class="text-gray-500 mb-6">Crea tu primer proyecto para comenzar</p>
                        <button id="createProjectBtn2" class="btn btn-primary">
                            <i class="fas fa-plus mr-2"></i>Crear Proyecto
                        </button>
                    </div>
                </div>
            `;
        }

        return this.projects.map(project => {
            const projectTasks = this.tasks.filter(t => t.projectId === project.id);
            const completedTasks = projectTasks.filter(t => t.completed).length;
            const progress = projectTasks.length > 0 ? (completedTasks / projectTasks.length) * 100 : 0;

            return `
                <div class="card project-card cursor-pointer hover:shadow-lg transition-all" data-project-id="${project.id}">
                    <div class="card-body">
                        <!-- Header -->
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex-1">
                                <h3 class="text-lg font-bold text-gray-900">
                                    ${this.escapeHtml(project.name)}
                                </h3>
                                <p class="text-sm text-gray-600 mt-1">
                                    ${this.escapeHtml(project.description || 'Sin descripción')}
                                </p>
                            </div>
                            <div class="flex space-x-1">
                                <button class="edit-project-btn text-blue-600 hover:text-blue-800 p-2" data-project-id="${project.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="delete-project-btn text-red-600 hover:text-red-800 p-2" data-project-id="${project.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Status badge -->
                        <div class="mb-3">
                            <span class="px-3 py-1 text-xs font-medium rounded-full ${project.completed ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}">
                                ${project.completed ? 'Completado' : 'En Progreso'}
                            </span>
                        </div>

                        <!-- Progress bar -->
                        <div class="mb-4">
                            <div class="flex justify-between items-center mb-2">
                                <span class="text-xs font-medium text-gray-700">Progreso</span>
                                <span class="text-xs font-semibold text-gray-900">${Math.round(progress)}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div class="bg-blue-600 h-2 rounded-full transition-all" style="width: ${progress}%"></div>
                            </div>
                        </div>

                        <!-- Detalles -->
                        <div class="space-y-2 mb-4 text-sm text-gray-600">
                            ${project.startDate ? `
                                <div class="flex items-center">
                                    <i class="fas fa-calendar-alt mr-2 text-gray-400 w-4"></i>
                                    <span>Inicio: ${this.formatDate(project.startDate)}</span>
                                </div>
                            ` : ''}
                            ${project.endDate ? `
                                <div class="flex items-center">
                                    <i class="fas fa-calendar-check mr-2 text-gray-400 w-4"></i>
                                    <span>Fin: ${this.formatDate(project.endDate)}</span>
                                </div>
                            ` : ''}
                            <div class="flex items-center">
                                <i class="fas fa-tasks mr-2 text-gray-400 w-4"></i>
                                <span>${completedTasks}/${projectTasks.length} tareas</span>
                            </div>
                        </div>

                        <!-- Team members -->
                        ${project.teamMembers && project.teamMembers.length > 0 ? `
                            <div class="mb-4 pb-4 border-t border-gray-200">
                                <p class="text-xs font-semibold text-gray-700 mb-2">Equipo (${project.teamMembers.length})</p>
                                <div class="flex flex-wrap gap-2">
                                    ${project.teamMembers.slice(0, 5).map(member => `
                                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
                                            ${member.charAt(0).toUpperCase()}${member.charAt(1).toUpperCase()}
                                        </span>
                                    `).join('')}
                                    ${project.teamMembers.length > 5 ? `
                                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">
                                            +${project.teamMembers.length - 5}
                                        </span>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Actions -->
                        <button class="view-project-btn w-full btn btn-secondary text-sm" data-project-id="${project.id}">
                            <i class="fas fa-eye mr-2"></i>Ver Detalles
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Crear proyecto
        const createBtns = this.container.querySelectorAll('#createProjectBtn, #createProjectBtn2');
        createBtns.forEach(btn => {
            btn.onclick = () => this.showCreateProjectModal();
        });

        // Ver detalles
        const viewBtns = this.container.querySelectorAll('.view-project-btn');
        viewBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const projectId = parseInt(btn.dataset.projectId);
                this.showProjectDetails(projectId);
            };
        });

        // Editar proyecto
        const editBtns = this.container.querySelectorAll('.edit-project-btn');
        editBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const projectId = parseInt(btn.dataset.projectId);
                this.showEditProjectModal(projectId);
            };
        });

        // Eliminar proyecto
        const deleteBtns = this.container.querySelectorAll('.delete-project-btn');
        deleteBtns.forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const projectId = parseInt(btn.dataset.projectId);
                this.showDeleteConfirmation(projectId);
            };
        });

        // Click en tarjeta de proyecto
        const projectCards = this.container.querySelectorAll('.project-card');
        projectCards.forEach(card => {
            card.onclick = (e) => {
                if (!e.target.closest('button')) {
                    const projectId = parseInt(card.dataset.projectId);
                    this.showProjectDetails(projectId);
                }
            };
        });
    }

    /**
     * Mostrar modal de crear proyecto
     */
    showCreateProjectModal() {
        // TODO: Implementar modal de creación
        console.log('Create project modal not implemented yet');
    }

    /**
     * Mostrar modal de editar proyecto
     */
    showEditProjectModal(projectId) {
        // TODO: Implementar modal de edición
        console.log('Edit project modal not implemented yet', projectId);
    }

    /**
     * Mostrar detalles de proyecto
     */
    showProjectDetails(projectId) {
        // TODO: Implementar vista de detalles
        console.log('Project details modal not implemented yet', projectId);
    }

    /**
     * Mostrar confirmación de eliminación
     */
    showDeleteConfirmation(projectId) {
        const project = this.projects.find(p => p.id === projectId);
        if (!project) return;

        this.showConfirm(
            `¿Está seguro de que desea eliminar el proyecto "${project.name}"?`,
            async () => {
                try {
                    await this.projectService.deleteProject(projectId);
                    this.projects = this.projects.filter(p => p.id !== projectId);
                    this.showSuccess('Proyecto eliminado exitosamente');
                    this.render();

                } catch (error) {
                    console.error('Error deleting project:', error);
                    this.showError('Error al eliminar el proyecto');
                }
            }
        );
    }
}