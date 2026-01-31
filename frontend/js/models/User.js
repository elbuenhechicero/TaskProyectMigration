/**
 * User Model - Maneja la lógica de usuarios
 */
class User extends BaseModel {
    constructor(data = {}) {
        super(data);
        this.username = data.username || '';
        this.email = data.email || '';
        this.password = data.password || ''; // En producción, esto no se debe exponer
        this.role = data.role || 'user';
        this.isActive = data.isActive !== undefined ? data.isActive : true;
        this.profile = data.profile || {
            firstName: '',
            lastName: '',
            avatar: null
        };
    }

    /**
     * Validaciones específicas del usuario
     */
    validate() {
        const errors = [];
        
        if (!this.username || this.username.length < 3) {
            errors.push('El nombre de usuario debe tener al menos 3 caracteres');
        }
        
        if (!this.email || !this.isValidEmail(this.email)) {
            errors.push('Debe proporcionar un email válido');
        }
        
        if (!this.password || this.password.length < 4) {
            errors.push('La contraseña debe tener al menos 4 caracteres');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validar formato de email
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Obtener nombre completo del usuario
     */
    getFullName() {
        if (this.profile.firstName && this.profile.lastName) {
            return `${this.profile.firstName} ${this.profile.lastName}`;
        }
        return this.username;
    }

    /**
     * Verificar si el usuario es admin
     */
    isAdmin() {
        return this.role === 'admin';
    }

    /**
     * Sanitizar datos para envío (sin password)
     */
    toSafeJSON() {
        const data = this.toJSON();
        delete data.password;
        return data;
    }
}