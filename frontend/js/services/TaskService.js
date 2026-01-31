/**
 * TaskService - Servicio para gestión de tareas
 */
class TaskService extends ApiService {
    constructor() {
        super();
        this.tasks = [];
    }

    /**
     * Obtener todas las tareas del usuario
     */
    async getAllTasks() {
        try {
            const response = await this.get('/api/v1/tasks');
            this.tasks = response.map(task => new Task(task));
            return this.tasks;
        } catch (error) {
            console.warn('API not available, using mock data:', error);
            return this.getMockTasks();
        }
    }

    /**
     * Obtener tarea por ID
     */
    async getTaskById(id) {
        try {
            const response = await this.get(`/api/v1/tasks/${id}`);
            return new Task(response);
        } catch (error) {
            console.warn('API not available, using mock data');
            const mockTasks = this.getMockTasks();
            return mockTasks.find(task => task.id === parseInt(id));
        }
    }

    /**
     * Crear nueva tarea
     */
    async createTask(taskData) {
        try {
            const response = await this.post('/api/v1/tasks', taskData);
            const newTask = new Task(response);
            this.tasks.push(newTask);
            return newTask;
        } catch (error) {
            console.warn('API not available, using mock creation');
            return this.mockCreateTask(taskData);
        }
    }

    /**
     * Actualizar tarea existente
     */
    async updateTask(id, taskData) {
        try {
            const response = await this.put(`/api/v1/tasks/${id}`, taskData);
            const updatedTask = new Task(response);
            
            const index = this.tasks.findIndex(task => task.id === id);
            if (index !== -1) {
                this.tasks[index] = updatedTask;
            }
            
            return updatedTask;
        } catch (error) {
            console.warn('API not available, using mock update');
            return this.mockUpdateTask(id, taskData);
        }
    }

    /**
     * Eliminar tarea
     */
    async deleteTask(id) {
        try {
            await this.delete(`/api/v1/tasks/${id}`);
            this.tasks = this.tasks.filter(task => task.id !== id);
            return { success: true, message: 'Tarea eliminada exitosamente' };
        } catch (error) {
            console.warn('API not available, using mock deletion');
            return this.mockDeleteTask(id);
        }
    }

    /**
     * Cambiar estado de tarea
     */
    async updateTaskStatus(id, status) {
        return this.updateTask(id, { status });
    }

    /**
     * Marcar tarea como completada
     */
    async completeTask(id) {
        try {
            const task = await this.getTaskById(id);
            task.markAsCompleted();
            return this.updateTask(id, task.toJSON());
        } catch (error) {
            console.error('Error completing task:', error);
            throw error;
        }
    }

    /**
     * Obtener tareas por proyecto
     */
    async getTasksByProject(projectId) {
        const allTasks = await this.getAllTasks();
        return allTasks.filter(task => task.projectId === projectId);
    }

    /**
     * Obtener tareas asignadas a un usuario
     */
    async getTasksByUser(userId) {
        const allTasks = await this.getAllTasks();
        return allTasks.filter(task => task.assignedTo === userId);
    }

    /**
     * Obtener tareas por estado
     */
    async getTasksByStatus(status) {
        const allTasks = await this.getAllTasks();
        return allTasks.filter(task => task.status === status);
    }

    /**
     * Buscar tareas por texto
     */
    async searchTasks(query) {
        const allTasks = await this.getAllTasks();
        const lowerQuery = query.toLowerCase();
        
        return allTasks.filter(task => 
            task.title.toLowerCase().includes(lowerQuery) ||
            task.description.toLowerCase().includes(lowerQuery) ||
            task.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
        );
    }

    /**
     * Obtener estadísticas de tareas
     */
    async getTaskStats() {
        const allTasks = await this.getAllTasks();
        
        return {
            total: allTasks.length,
            completed: allTasks.filter(t => t.completed).length,
            pending: allTasks.filter(t => t.status === 'Pendiente').length,
            inProgress: allTasks.filter(t => t.status === 'En Progreso').length,
            overdue: allTasks.filter(t => t.isOverdue()).length
        };
    }

    // ============ MÉTODOS MOCK (Para desarrollo local) ============

    getMockTasks() {
        const mockData = [
            {
                id: 1,
                title: 'Implementar autenticación',
                description: 'Desarrollar sistema de login y registro',
                status: 'En Progreso',
                priority: 'Alta',
                projectId: 1,
                assignedTo: 1,
                dueDate: '2026-02-15',
                estimatedHours: 8,
                actualHours: 5,
                tags: ['backend', 'security']
            },
            {
                id: 2,
                title: 'Diseño de interfaz',
                description: 'Crear mockups de la aplicación',
                status: 'Completada',
                priority: 'Media',
                projectId: 1,
                assignedTo: 2,
                dueDate: '2026-02-10',
                estimatedHours: 12,
                actualHours: 10,
                tags: ['frontend', 'design']
            },
            {
                id: 3,
                title: 'Configurar base de datos',
                description: 'Instalar y configurar MongoDB',
                status: 'Pendiente',
                priority: 'Crítica',
                projectId: 2,
                assignedTo: 1,
                dueDate: '2026-02-05',
                estimatedHours: 4,
                tags: ['database', 'setup']
            }
        ];

        this.tasks = mockData.map(task => new Task(task));
        return this.tasks;
    }

    mockCreateTask(taskData) {
        const newTask = new Task({
            ...taskData,
            id: Math.max(...this.tasks.map(t => t.id)) + 1
        });
        
        this.tasks.push(newTask);
        return newTask;
    }

    mockUpdateTask(id, taskData) {
        const index = this.tasks.findIndex(task => task.id === parseInt(id));
        if (index !== -1) {
            this.tasks[index].update(taskData);
            return this.tasks[index];
        }
        throw new Error('Tarea no encontrada');
    }

    mockDeleteTask(id) {
        const index = this.tasks.findIndex(task => task.id === parseInt(id));
        if (index !== -1) {
            this.tasks.splice(index, 1);
            return { success: true, message: 'Tarea eliminada exitosamente' };
        }
        throw new Error('Tarea no encontrada');
    }
}