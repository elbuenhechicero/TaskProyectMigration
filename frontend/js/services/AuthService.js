/**
 * AuthService - Servicio de autenticación
 * Maneja login, registro, tokens y sesiones
 */
class AuthService extends ApiService {
    constructor() {
        super();
        this.currentUser = null;
        this.loadCurrentUser();
    }

    /**
     * Cargar usuario actual desde localStorage
     */
    loadCurrentUser() {
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            try {
                const data = JSON.parse(userData);
                this.currentUser = new User(data);
            } catch (error) {
                console.error('Error loading current user:', error);
                localStorage.removeItem('currentUser');
            }
        }
    }

    /**
     * Guardar usuario actual en localStorage
     */
    saveCurrentUser(userData) {
        this.currentUser = new User(userData);
        localStorage.setItem('currentUser', JSON.stringify(userData));
    }

    /**
     * Realizar login
     */
    async login(username, password) {
        try {
            const response = await this.post('/api/v1/auth/login', {
                username,
                password
            }, false);

            // Guardar token y usuario
            this.setAuthToken(response.access_token);
            this.saveCurrentUser(response.user);

            return {
                success: true,
                user: this.currentUser,
                token: response.access_token
            };

        } catch (error) {
            console.error('Login error:', error);
            
            // Fallback para desarrollo local (eliminar en producción)
            if (error.status === 0 || error.message.includes('conectar')) {
                return this.mockLogin(username, password);
            }
            
            throw error;
        }
    }

    /**
     * Mock login para desarrollo (eliminar en producción)
     */
    mockLogin(username, password) {
        const mockUsers = [
            { id: 1, username: 'admin', password: 'admin', role: 'admin' },
            { id: 2, username: 'user1', password: 'user1', role: 'user' },
            { id: 3, username: 'user2', password: 'user2', role: 'user' }
        ];

        const user = mockUsers.find(u => u.username === username && u.password === password);
        
        if (user) {
            const userData = {
                ...user,
                email: `${username}@example.com`,
                profile: { firstName: username, lastName: 'User' }
            };
            
            this.saveCurrentUser(userData);
            this.setAuthToken('mock-token-' + Date.now());
            
            return {
                success: true,
                user: this.currentUser,
                token: this.token
            };
        }
        
        throw new ApiError('Credenciales inválidas', 401);
    }

    /**
     * Realizar registro
     */
    async register(userData) {
        try {
            const response = await this.post('/api/v1/auth/register', userData, false);
            
            this.setAuthToken(response.access_token);
            this.saveCurrentUser(response.user);

            return {
                success: true,
                user: this.currentUser,
                token: response.access_token
            };

        } catch (error) {
            console.error('Register error:', error);
            throw error;
        }
    }

    /**
     * Cerrar sesión
     */
    async logout() {
        try {
            if (this.token && !this.token.startsWith('mock-token')) {
                await this.post('/api/v1/auth/logout');
            }
        } catch (error) {
            console.warn('Error during server logout:', error);
        } finally {
            // Limpiar datos locales
            this.setAuthToken(null);
            this.currentUser = null;
            localStorage.removeItem('currentUser');
        }
    }

    /**
     * Refrescar token
     */
    async refreshToken() {
        try {
            const response = await this.post('/api/v1/auth/refresh');
            this.setAuthToken(response.access_token);
            return response.access_token;
        } catch (error) {
            console.error('Token refresh error:', error);
            await this.logout();
            throw error;
        }
    }

    /**
     * Verificar si el usuario está autenticado
     */
    isAuthenticated() {
        return !!(this.token && this.currentUser);
    }

    /**
     * Obtener usuario actual
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * Verificar si el usuario actual es administrador
     */
    isAdmin() {
        return this.currentUser && this.currentUser.isAdmin();
    }

    /**
     * Cambiar contraseña
     */
    async changePassword(currentPassword, newPassword) {
        try {
            await this.put('/api/v1/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });

            return { success: true, message: 'Contraseña cambiada exitosamente' };

        } catch (error) {
            console.error('Change password error:', error);
            throw error;
        }
    }

    /**
     * Solicitar restablecimiento de contraseña
     */
    async requestPasswordReset(email) {
        try {
            await this.post('/api/v1/auth/password-reset-request', { email }, false);
            return { success: true, message: 'Se ha enviado un enlace de restablecimiento a su email' };
        } catch (error) {
            console.error('Password reset request error:', error);
            throw error;
        }
    }

    /**
     * Actualizar perfil de usuario
     */
    async updateProfile(profileData) {
        try {
            const response = await this.put('/api/v1/auth/profile', profileData);
            this.saveCurrentUser(response.user);
            
            return {
                success: true,
                user: this.currentUser,
                message: 'Perfil actualizado exitosamente'
            };

        } catch (error) {
            console.error('Update profile error:', error);
            throw error;
        }
    }

    /**
     * Validar sesión al iniciar la aplicación
     */
    async validateSession() {
        if (!this.isAuthenticated()) {
            return false;
        }

        try {
            // Solo validar si no es token mock
            if (!this.token.startsWith('mock-token')) {
                await this.validateToken();
            }
            return true;
        } catch (error) {
            console.warn('Session validation failed:', error);
            await this.logout();
            return false;
        }
    }
}