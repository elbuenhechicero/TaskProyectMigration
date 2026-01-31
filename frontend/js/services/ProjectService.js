/**
 * ProjectService - Servicio para gestión de proyectos
 */
class ProjectService extends ApiService {
    constructor() {
        super();
        this.projects = [];
    }

    /**
     * Obtener todos los proyectos
     */
    async getAllProjects() {
        try {
            const response = await this.get('/api/v1/projects');
            this.projects = response.map(project => new Project(project));
            return this.projects;
        } catch (error) {
            console.warn('API not available, using mock data:', error);
            return this.getMockProjects();
        }
    }

    /**
     * Obtener proyecto por ID
     */
    async getProjectById(id) {
        try {
            const response = await this.get(`/api/v1/projects/${id}`);
            return new Project(response);
        } catch (error) {
            console.warn('API not available, using mock data');
            const mockProjects = this.getMockProjects();
            return mockProjects.find(project => project.id === parseInt(id));
        }
    }

    /**
     * Crear nuevo proyecto
     */
    async createProject(projectData) {
        try {
            const response = await this.post('/api/v1/projects', projectData);
            const newProject = new Project(response);
            this.projects.push(newProject);
            return newProject;
        } catch (error) {
            console.warn('API not available, using mock creation');
            return this.mockCreateProject(projectData);
        }
    }

    /**
     * Actualizar proyecto existente
     */
    async updateProject(id, projectData) {
        try {
            const response = await this.put(`/api/v1/projects/${id}`, projectData);
            const updatedProject = new Project(response);
            
            const index = this.projects.findIndex(project => project.id === id);
            if (index !== -1) {
                this.projects[index] = updatedProject;
            }
            
            return updatedProject;
        } catch (error) {
            console.warn('API not available, using mock update');
            return this.mockUpdateProject(id, projectData);
        }
    }

    /**
     * Eliminar proyecto
     */
    async deleteProject(id) {
        try {
            await this.delete(`/api/v1/projects/${id}`);
            this.projects = this.projects.filter(project => project.id !== id);
            return { success: true, message: 'Proyecto eliminado exitosamente' };
        } catch (error) {
            console.warn('API not available, using mock deletion');
            return this.mockDeleteProject(id);
        }
    }

    /**
     * Agregar miembro al equipo del proyecto
     */
    async addTeamMember(projectId, userId) {
        try {
            const response = await this.post(`/api/v1/projects/${projectId}/team`, { userId });
            return response;
        } catch (error) {
            console.warn('API not available, using mock operation');
            const project = this.projects.find(p => p.id === projectId);
            if (project) {
                project.addTeamMember(userId);
                return { success: true, message: 'Miembro agregado al equipo' };
            }
            throw new Error('Proyecto no encontrado');
        }
    }

    /**
     * Remover miembro del equipo
     */
    async removeTeamMember(projectId, userId) {
        try {
            await this.delete(`/api/v1/projects/${projectId}/team/${userId}`);
            return { success: true, message: 'Miembro removido del equipo' };
        } catch (error) {
            console.warn('API not available, using mock operation');
            const project = this.projects.find(p => p.id === projectId);
            if (project) {
                project.removeTeamMember(userId);
                return { success: true, message: 'Miembro removido del equipo' };
            }
            throw new Error('Proyecto no encontrado');
        }
    }

    /**
     * Obtener proyectos por usuario
     */
    async getProjectsByUser(userId) {
        const allProjects = await this.getAllProjects();
        return allProjects.filter(project => 
            project.ownerId === userId || project.isTeamMember(userId)
        );
    }

    /**
     * Obtener estadísticas del proyecto
     */
    async getProjectStats(projectId) {
        try {
            const response = await this.get(`/api/v1/projects/${projectId}/stats`);
            return response;
        } catch (error) {
            console.warn('API not available, using mock stats');
            return this.mockGetProjectStats(projectId);
        }
    }

    /**
     * Actualizar progreso del proyecto
     */
    async updateProjectProgress(projectId, progress) {
        return this.updateProject(projectId, { progress });
    }

    /**
     * Cambiar estado del proyecto
     */
    async updateProjectStatus(projectId, status) {
        return this.updateProject(projectId, { status });
    }

    /**
     * Buscar proyectos
     */
    async searchProjects(query) {
        const allProjects = await this.getAllProjects();
        const lowerQuery = query.toLowerCase();
        
        return allProjects.filter(project => 
            project.name.toLowerCase().includes(lowerQuery) ||
            project.description.toLowerCase().includes(lowerQuery) ||
            project.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
        );
    }

    // ============ MÉTODOS MOCK (Para desarrollo local) ============

    getMockProjects() {
        const mockData = [
            {
                id: 1,
                name: 'Sistema de Gestión de Tareas',
                description: 'Aplicación web para gestión de proyectos y tareas',
                status: 'Activo',
                startDate: '2026-01-01',
                endDate: '2026-03-31',
                budget: 50000,
                ownerId: 1,
                teamMembers: [1, 2],
                tags: ['web', 'javascript', 'mongodb'],
                progress: 35,
                color: '#3B82F6'
            },
            {
                id: 2,
                name: 'API REST Backend',
                description: 'Desarrollo de API para aplicaciones móviles',
                status: 'En Pausa',
                startDate: '2026-02-01',
                endDate: '2026-04-30',
                budget: 30000,
                ownerId: 2,
                teamMembers: [2, 3],
                tags: ['api', 'python', 'fastapi'],
                progress: 15,
                color: '#10B981'
            },
            {
                id: 3,
                name: 'Migración de Datos',
                description: 'Migrar sistema legacy a nueva arquitectura',
                status: 'Completado',
                startDate: '2025-11-01',
                endDate: '2026-01-15',
                budget: 25000,
                ownerId: 1,
                teamMembers: [1],
                tags: ['migration', 'database'],
                progress: 100,
                color: '#F59E0B'
            }
        ];

        this.projects = mockData.map(project => new Project(project));
        return this.projects;
    }

    mockCreateProject(projectData) {
        const newProject = new Project({
            ...projectData,
            id: Math.max(...this.projects.map(p => p.id)) + 1
        });
        
        this.projects.push(newProject);
        return newProject;
    }

    mockUpdateProject(id, projectData) {
        const index = this.projects.findIndex(project => project.id === parseInt(id));
        if (index !== -1) {
            this.projects[index].update(projectData);
            return this.projects[index];
        }
        throw new Error('Proyecto no encontrado');
    }

    mockDeleteProject(id) {
        const index = this.projects.findIndex(project => project.id === parseInt(id));
        if (index !== -1) {
            this.projects.splice(index, 1);
            return { success: true, message: 'Proyecto eliminado exitosamente' };
        }
        throw new Error('Proyecto no encontrado');
    }

    mockGetProjectStats(projectId) {
        // Simular estadísticas del proyecto
        return {
            totalTasks: 15,
            completedTasks: 8,
            pendingTasks: 5,
            inProgressTasks: 2,
            totalHours: 120,
            budgetUsed: 18500,
            teamSize: 3
        };
    }
}