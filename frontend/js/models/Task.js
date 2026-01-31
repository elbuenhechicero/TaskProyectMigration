/**
 * Task Model - Maneja la lógica de tareas
 */
class Task extends BaseModel {
    constructor(data = {}) {
        super(data);
        this.title = data.title || '';
        this.description = data.description || '';
        this.status = data.status || 'Pendiente';
        this.priority = data.priority || 'Media';
        this.projectId = data.projectId || null;
        this.assignedTo = data.assignedTo || null;
        this.dueDate = data.dueDate || null;
        this.estimatedHours = data.estimatedHours || 0;
        this.actualHours = data.actualHours || 0;
        this.tags = data.tags || [];
        this.completed = data.completed || false;
        this.completedAt = data.completedAt || null;
    }

    /**
     * Estados válidos para las tareas
     */
    static get VALID_STATUSES() {
        return ['Pendiente', 'En Progreso', 'Completada', 'Bloqueada', 'Cancelada'];
    }

    /**
     * Prioridades válidas
     */
    static get VALID_PRIORITIES() {
        return ['Baja', 'Media', 'Alta', 'Crítica'];
    }

    /**
     * Validaciones específicas de tareas
     */
    validate() {
        const errors = [];
        
        if (!this.title || this.title.trim().length === 0) {
            errors.push('El título es obligatorio');
        }
        
        if (this.title && this.title.length > 100) {
            errors.push('El título no puede exceder 100 caracteres');
        }
        
        if (!Task.VALID_STATUSES.includes(this.status)) {
            errors.push('Estado de tarea inválido');
        }
        
        if (!Task.VALID_PRIORITIES.includes(this.priority)) {
            errors.push('Prioridad de tarea inválida');
        }
        
        if (this.dueDate && new Date(this.dueDate) < new Date()) {
            errors.push('La fecha de vencimiento no puede ser en el pasado');
        }
        
        if (this.estimatedHours < 0) {
            errors.push('Las horas estimadas no pueden ser negativas');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Marcar tarea como completada
     */
    markAsCompleted() {
        this.status = 'Completada';
        this.completed = true;
        this.completedAt = new Date().toISOString();
        this.updatedAt = new Date().toISOString();
    }

    /**
     * Verificar si la tarea está vencida
     */
    isOverdue() {
        if (!this.dueDate || this.completed) return false;
        return new Date(this.dueDate) < new Date();
    }

    /**
     * Obtener progreso de la tarea
     */
    getProgress() {
        if (this.completed) return 100;
        
        switch (this.status) {
            case 'Pendiente': return 0;
            case 'En Progreso': return 50;
            case 'Completada': return 100;
            case 'Bloqueada': return 25;
            case 'Cancelada': return 0;
            default: return 0;
        }
    }

    /**
     * Obtener clase CSS basada en prioridad
     */
    getPriorityClass() {
        const priorityClasses = {
            'Baja': 'priority-low',
            'Media': 'priority-medium',
            'Alta': 'priority-high',
            'Crítica': 'priority-critical'
        };
        return priorityClasses[this.priority] || 'priority-medium';
    }

    /**
     * Obtener días restantes hasta vencimiento
     */
    getDaysUntilDue() {
        if (!this.dueDate) return null;
        const today = new Date();
        const due = new Date(this.dueDate);
        const diffTime = due - today;
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }
}