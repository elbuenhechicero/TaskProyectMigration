/**
 * Project Model - Maneja la lógica de proyectos
 */
class Project extends BaseModel {
    constructor(data = {}) {
        super(data);
        this.name = data.name || '';
        this.description = data.description || '';
        this.status = data.status || 'Activo';
        this.startDate = data.startDate || null;
        this.endDate = data.endDate || null;
        this.budget = data.budget || 0;
        this.ownerId = data.ownerId || null;
        this.teamMembers = data.teamMembers || [];
        this.tags = data.tags || [];
        this.progress = data.progress || 0;
        this.color = data.color || '#3B82F6';
    }

    /**
     * Estados válidos para proyectos
     */
    static get VALID_STATUSES() {
        return ['Activo', 'En Pausa', 'Completado', 'Cancelado', 'Archivado'];
    }

    /**
     * Validaciones específicas de proyectos
     */
    validate() {
        const errors = [];
        
        if (!this.name || this.name.trim().length === 0) {
            errors.push('El nombre del proyecto es obligatorio');
        }
        
        if (this.name && this.name.length > 80) {
            errors.push('El nombre no puede exceder 80 caracteres');
        }
        
        if (!Project.VALID_STATUSES.includes(this.status)) {
            errors.push('Estado de proyecto inválido');
        }
        
        if (this.startDate && this.endDate) {
            if (new Date(this.startDate) > new Date(this.endDate)) {
                errors.push('La fecha de inicio no puede ser posterior a la fecha de fin');
            }
        }
        
        if (this.budget < 0) {
            errors.push('El presupuesto no puede ser negativo');
        }
        
        if (this.progress < 0 || this.progress > 100) {
            errors.push('El progreso debe estar entre 0 y 100');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Agregar miembro al equipo
     */
    addTeamMember(userId) {
        if (!this.teamMembers.includes(userId)) {
            this.teamMembers.push(userId);
            this.updatedAt = new Date().toISOString();
        }
    }

    /**
     * Remover miembro del equipo
     */
    removeTeamMember(userId) {
        const index = this.teamMembers.indexOf(userId);
        if (index > -1) {
            this.teamMembers.splice(index, 1);
            this.updatedAt = new Date().toISOString();
        }
    }

    /**
     * Verificar si el usuario es miembro del equipo
     */
    isTeamMember(userId) {
        return this.teamMembers.includes(userId) || this.ownerId === userId;
    }

    /**
     * Calcular duración del proyecto en días
     */
    getDuration() {
        if (!this.startDate || !this.endDate) return null;
        const start = new Date(this.startDate);
        const end = new Date(this.endDate);
        const diffTime = end - start;
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    /**
     * Verificar si el proyecto está retrasado
     */
    isOverdue() {
        if (!this.endDate || this.status === 'Completado') return false;
        return new Date(this.endDate) < new Date();
    }

    /**
     * Obtener estado visual del proyecto
     */
    getStatusInfo() {
        const statusInfo = {
            'Activo': { class: 'status-active', icon: 'play', color: '#10B981' },
            'En Pausa': { class: 'status-paused', icon: 'pause', color: '#F59E0B' },
            'Completado': { class: 'status-completed', icon: 'check', color: '#059669' },
            'Cancelado': { class: 'status-cancelled', icon: 'x', color: '#DC2626' },
            'Archivado': { class: 'status-archived', icon: 'archive', color: '#6B7280' }
        };
        return statusInfo[this.status] || statusInfo['Activo'];
    }

    /**
     * Marcar proyecto como completado
     */
    markAsCompleted() {
        this.status = 'Completado';
        this.progress = 100;
        this.updatedAt = new Date().toISOString();
    }
}