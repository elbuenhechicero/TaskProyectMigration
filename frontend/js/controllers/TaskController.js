/**
 * TaskController - Controlador de tareas
 */
class TaskController {
    constructor(taskService, projectService, taskView) {
        this.taskService = taskService;
        this.projectService = projectService;
        this.taskView = taskView;
        this.init();
    }

    /**
     * Inicializar controlador
     */
    init() {
        this.setupEventListeners();
    }

    /**
     * Configurar event listeners globales de tareas
     */
    setupEventListeners() {
        // Escuchar eventos de navegación hacia tareas
        window.addEventListener('navigate-to-tasks', (e) => {
            this.showTasks();
        });

        // Escuchar eventos de creación de tarea
        window.addEventListener('task-created', (e) => {
            this.onTaskCreated(e.detail);
        });

        // Escuchar eventos de actualización de tarea
        window.addEventListener('task-updated', (e) => {
            this.onTaskUpdated(e.detail);
        });

        // Escuchar eventos de eliminación de tarea
        window.addEventListener('task-deleted', (e) => {
            this.onTaskDeleted(e.detail);
        });
    }

    /**
     * Mostrar vista de tareas
     */
    async showTasks(filters = {}) {
        try {
            await this.taskView.render(filters);
        } catch (error) {
            console.error('Error showing tasks:', error);
        }
    }

    /**
     * Crear nueva tarea
     */
    async createTask(taskData) {
        try {
            const task = new Task(taskData);
            
            // Validar datos
            if (!task.validate()) {
                throw new Error('Invalid task data');
            }

            // Guardar en servicio
            const newTask = await this.taskService.createTask(task);
            
            // Disparar evento
            window.dispatchEvent(new CustomEvent('task-created', { detail: newTask }));
            
            return newTask;

        } catch (error) {
            console.error('Error creating task:', error);
            throw error;
        }
    }

    /**
     * Actualizar tarea
     */
    async updateTask(taskId, updatedData) {
        try {
            const task = new Task({ id: taskId, ...updatedData });
            
            // Validar datos
            if (!task.validate()) {
                throw new Error('Invalid task data');
            }

            // Guardar cambios
            const updatedTask = await this.taskService.updateTask(taskId, task);
            
            // Disparar evento
            window.dispatchEvent(new CustomEvent('task-updated', { detail: updatedTask }));
            
            return updatedTask;

        } catch (error) {
            console.error('Error updating task:', error);
            throw error;
        }
    }

    /**
     * Completar tarea
     */
    async completeTask(taskId) {
        try {
            const task = await this.taskService.getTaskById(taskId);
            if (!task) throw new Error('Task not found');

            task.markAsCompleted();
            const updatedTask = await this.taskService.updateTask(taskId, task);

            window.dispatchEvent(new CustomEvent('task-updated', { detail: updatedTask }));
            
            return updatedTask;

        } catch (error) {
            console.error('Error completing task:', error);
            throw error;
        }
    }

    /**
     * Eliminar tarea
     */
    async deleteTask(taskId) {
        try {
            await this.taskService.deleteTask(taskId);
            window.dispatchEvent(new CustomEvent('task-deleted', { detail: { id: taskId } }));

        } catch (error) {
            console.error('Error deleting task:', error);
            throw error;
        }
    }

    /**
     * Manejar tarea creada
     */
    onTaskCreated(taskData) {
        console.log('Task created:', taskData);
        this.showTasks();
    }

    /**
     * Manejar tarea actualizada
     */
    onTaskUpdated(taskData) {
        console.log('Task updated:', taskData);
        this.showTasks();
    }

    /**
     * Manejar tarea eliminada
     */
    onTaskDeleted(data) {
        console.log('Task deleted:', data);
        this.showTasks();
    }

    /**
     * Obtener estadísticas de tareas
     */
    async getTaskStats() {
        try {
            return await this.taskService.getTaskStats();
        } catch (error) {
            console.error('Error getting task stats:', error);
            return {};
        }
    }

    /**
     * Obtener tareas por proyecto
     */
    async getTasksByProject(projectId) {
        try {
            return await this.taskService.getTasksByProject(projectId);
        } catch (error) {
            console.error('Error getting tasks by project:', error);
            return [];
        }
    }

    /**
     * Obtener tareas vencidas
     */
    async getOverdueTasks() {
        try {
            const allTasks = await this.taskService.getAllTasks();
            return allTasks.filter(task => task.isOverdue() && !task.completed);
        } catch (error) {
            console.error('Error getting overdue tasks:', error);
            return [];
        }
    }

    /**
     * Obtener tareas urgentes
     */
    async getUrgentTasks() {
        try {
            const allTasks = await this.taskService.getAllTasks();
            return allTasks.filter(task => task.priority === 'Crítica' && !task.completed);
        } catch (error) {
            console.error('Error getting urgent tasks:', error);
            return [];
        }
    }

    /**
     * Asignar tarea a usuario
     */
    async assignTask(taskId, userId) {
        try {
            const task = await this.taskService.getTaskById(taskId);
            if (!task) throw new Error('Task not found');

            task.assignedTo = userId;
            const updatedTask = await this.taskService.updateTask(taskId, task);

            window.dispatchEvent(new CustomEvent('task-updated', { detail: updatedTask }));
            
            return updatedTask;

        } catch (error) {
            console.error('Error assigning task:', error);
            throw error;
        }
    }

    /**
     * Cambiar prioridad de tarea
     */
    async changePriority(taskId, priority) {
        try {
            if (!Task.VALID_PRIORITIES.includes(priority)) {
                throw new Error('Invalid priority');
            }

            const task = await this.taskService.getTaskById(taskId);
            if (!task) throw new Error('Task not found');

            task.priority = priority;
            const updatedTask = await this.taskService.updateTask(taskId, task);

            window.dispatchEvent(new CustomEvent('task-updated', { detail: updatedTask }));
            
            return updatedTask;

        } catch (error) {
            console.error('Error changing priority:', error);
            throw error;
        }
    }

    /**
     * Cambiar estado de tarea
     */
    async changeStatus(taskId, status) {
        try {
            if (!Task.VALID_STATUSES.includes(status)) {
                throw new Error('Invalid status');
            }

            const task = await this.taskService.getTaskById(taskId);
            if (!task) throw new Error('Task not found');

            task.status = status;
            const updatedTask = await this.taskService.updateTask(taskId, task);

            window.dispatchEvent(new CustomEvent('task-updated', { detail: updatedTask }));
            
            return updatedTask;

        } catch (error) {
            console.error('Error changing status:', error);
            throw error;
        }
    }
}