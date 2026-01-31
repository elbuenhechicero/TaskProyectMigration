/**
 * ProjectController - Controlador de proyectos
 */
class ProjectController {
    constructor(projectService, taskService, projectView) {
        this.projectService = projectService;
        this.taskService = taskService;
        this.projectView = projectView;
        this.init();
    }

    /**
     * Inicializar controlador
     */
    init() {
        this.setupEventListeners();
    }

    /**
     * Configurar event listeners globales de proyectos
     */
    setupEventListeners() {
        // Escuchar eventos de navegación hacia proyectos
        window.addEventListener('navigate-to-projects', (e) => {
            this.showProjects();
        });

        // Escuchar eventos de creación de proyecto
        window.addEventListener('project-created', (e) => {
            this.onProjectCreated(e.detail);
        });

        // Escuchar eventos de actualización de proyecto
        window.addEventListener('project-updated', (e) => {
            this.onProjectUpdated(e.detail);
        });

        // Escuchar eventos de eliminación de proyecto
        window.addEventListener('project-deleted', (e) => {
            this.onProjectDeleted(e.detail);
        });
    }

    /**
     * Mostrar vista de proyectos
     */
    async showProjects(selectedProjectId = null) {
        try {
            await this.projectView.render(selectedProjectId);
        } catch (error) {
            console.error('Error showing projects:', error);
        }
    }

    /**
     * Crear nuevo proyecto
     */
    async createProject(projectData) {
        try {
            const project = new Project(projectData);
            
            // Validar datos
            if (!project.validate()) {
                throw new Error('Invalid project data');
            }

            // Guardar en servicio
            const newProject = await this.projectService.createProject(project);
            
            // Disparar evento
            window.dispatchEvent(new CustomEvent('project-created', { detail: newProject }));
            
            return newProject;

        } catch (error) {
            console.error('Error creating project:', error);
            throw error;
        }
    }

    /**
     * Actualizar proyecto
     */
    async updateProject(projectId, updatedData) {
        try {
            const project = new Project({ id: projectId, ...updatedData });
            
            // Validar datos
            if (!project.validate()) {
                throw new Error('Invalid project data');
            }

            // Guardar cambios
            const updatedProject = await this.projectService.updateProject(projectId, project);
            
            // Disparar evento
            window.dispatchEvent(new CustomEvent('project-updated', { detail: updatedProject }));
            
            return updatedProject;

        } catch (error) {
            console.error('Error updating project:', error);
            throw error;
        }
    }

    /**
     * Completar proyecto
     */
    async completeProject(projectId) {
        try {
            const project = await this.projectService.getProjectById(projectId);
            if (!project) throw new Error('Project not found');

            project.markAsCompleted();
            const updatedProject = await this.projectService.updateProject(projectId, project);

            window.dispatchEvent(new CustomEvent('project-updated', { detail: updatedProject }));
            
            return updatedProject;

        } catch (error) {
            console.error('Error completing project:', error);
            throw error;
        }
    }

    /**
     * Eliminar proyecto
     */
    async deleteProject(projectId) {
        try {
            await this.projectService.deleteProject(projectId);
            window.dispatchEvent(new CustomEvent('project-deleted', { detail: { id: projectId } }));

        } catch (error) {
            console.error('Error deleting project:', error);
            throw error;
        }
    }

    /**
     * Manejar proyecto creado
     */
    onProjectCreated(projectData) {
        console.log('Project created:', projectData);
        this.showProjects();
    }

    /**
     * Manejar proyecto actualizado
     */
    onProjectUpdated(projectData) {
        console.log('Project updated:', projectData);
        this.showProjects();
    }

    /**
     * Manejar proyecto eliminado
     */
    onProjectDeleted(data) {
        console.log('Project deleted:', data);
        this.showProjects();
    }

    /**
     * Obtener estadísticas de proyectos
     */
    async getProjectStats() {
        try {
            return await this.projectService.getProjectStats();
        } catch (error) {
            console.error('Error getting project stats:', error);
            return {};
        }
    }

    /**
     * Obtener proyectos activos
     */
    async getActiveProjects() {
        try {
            const allProjects = await this.projectService.getAllProjects();
            return allProjects.filter(project => !project.completed);
        } catch (error) {
            console.error('Error getting active projects:', error);
            return [];
        }
    }

    /**
     * Obtener proyectos completados
     */
    async getCompletedProjects() {
        try {
            const allProjects = await this.projectService.getAllProjects();
            return allProjects.filter(project => project.completed);
        } catch (error) {
            console.error('Error getting completed projects:', error);
            return [];
        }
    }

    /**
     * Agregar miembro al equipo
     */
    async addTeamMember(projectId, memberEmail) {
        try {
            const project = await this.projectService.getProjectById(projectId);
            if (!project) throw new Error('Project not found');

            project.addTeamMember(memberEmail);
            const updatedProject = await this.projectService.updateProject(projectId, project);

            window.dispatchEvent(new CustomEvent('project-updated', { detail: updatedProject }));
            
            return updatedProject;

        } catch (error) {
            console.error('Error adding team member:', error);
            throw error;
        }
    }

    /**
     * Remover miembro del equipo
     */
    async removeTeamMember(projectId, memberEmail) {
        try {
            const project = await this.projectService.getProjectById(projectId);
            if (!project) throw new Error('Project not found');

            project.removeTeamMember(memberEmail);
            const updatedProject = await this.projectService.updateProject(projectId, project);

            window.dispatchEvent(new CustomEvent('project-updated', { detail: updatedProject }));
            
            return updatedProject;

        } catch (error) {
            console.error('Error removing team member:', error);
            throw error;
        }
    }

    /**
     * Obtener tareas del proyecto
     */
    async getProjectTasks(projectId) {
        try {
            return await this.taskService.getTasksByProject(projectId);
        } catch (error) {
            console.error('Error getting project tasks:', error);
            return [];
        }
    }

    /**
     * Obtener progreso del proyecto
     */
    async getProjectProgress(projectId) {
        try {
            const tasks = await this.getProjectTasks(projectId);
            const completedTasks = tasks.filter(t => t.completed).length;
            
            return {
                total: tasks.length,
                completed: completedTasks,
                percentage: tasks.length > 0 ? (completedTasks / tasks.length) * 100 : 0,
                remaining: tasks.length - completedTasks
            };

        } catch (error) {
            console.error('Error getting project progress:', error);
            return {
                total: 0,
                completed: 0,
                percentage: 0,
                remaining: 0
            };
        }
    }

    /**
     * Obtener proyectos vencidos
     */
    async getOverdueProjects() {
        try {
            const allProjects = await this.projectService.getAllProjects();
            return allProjects.filter(project => project.isOverdue() && !project.completed);
        } catch (error) {
            console.error('Error getting overdue projects:', error);
            return [];
        }
    }

    /**
     * Cambiar fecha de fin
     */
    async changeEndDate(projectId, newEndDate) {
        try {
            const project = await this.projectService.getProjectById(projectId);
            if (!project) throw new Error('Project not found');

            project.endDate = new Date(newEndDate);
            const updatedProject = await this.projectService.updateProject(projectId, project);

            window.dispatchEvent(new CustomEvent('project-updated', { detail: updatedProject }));
            
            return updatedProject;

        } catch (error) {
            console.error('Error changing end date:', error);
            throw error;
        }
    }
}