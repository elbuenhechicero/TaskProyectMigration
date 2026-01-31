/**
 * ApiService - Servicio base para comunicación con la API
 * Maneja autenticación, peticiones HTTP y manejo de errores
 */
class ApiService {
    constructor() {
        // Detectar automáticamente si estamos en producción o desarrollo
        this.baseURL = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : 'https://taskmanager-api.onrender.com';
        this.token = localStorage.getItem('authToken');
    }

    /**
     * Configurar el token de autenticación
     */
    setAuthToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }

    /**
     * Obtener headers por defecto
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * Hacer petición HTTP genérica
     */
    async request(method, endpoint, data = null, includeAuth = true) {
        try {
            const config = {
                method: method.toUpperCase(),
                headers: this.getHeaders(includeAuth)
            };

            if (data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            // Manejar errores HTTP
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new ApiError(
                    errorData.message || `HTTP ${response.status}`,
                    response.status,
                    errorData
                );
            }

            // Intentar parsear JSON, si no es posible, devolver texto
            try {
                return await response.json();
            } catch {
                return await response.text();
            }

        } catch (error) {
            console.error(`API Request Error [${method.toUpperCase()} ${endpoint}]:`, error);
            
            // Si no hay conexión a internet
            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                throw new ApiError('No se pudo conectar con el servidor. Verifique su conexión a internet.', 0);
            }
            
            // Re-lanzar errores conocidos
            if (error instanceof ApiError) {
                throw error;
            }
            
            // Error desconocido
            throw new ApiError('Error inesperado al comunicarse con el servidor', 500, error);
        }
    }

    /**
     * Métodos HTTP específicos
     */
    async get(endpoint, includeAuth = true) {
        return this.request('GET', endpoint, null, includeAuth);
    }

    async post(endpoint, data, includeAuth = true) {
        return this.request('POST', endpoint, data, includeAuth);
    }

    async put(endpoint, data, includeAuth = true) {
        return this.request('PUT', endpoint, data, includeAuth);
    }

    async patch(endpoint, data, includeAuth = true) {
        return this.request('PATCH', endpoint, data, includeAuth);
    }

    async delete(endpoint, includeAuth = true) {
        return this.request('DELETE', endpoint, null, includeAuth);
    }

    /**
     * Verificar si el token es válido
     */
    async validateToken() {
        try {
            await this.get('/api/v1/auth/validate');
            return true;
        } catch (error) {
            if (error.status === 401) {
                this.setAuthToken(null);
                return false;
            }
            throw error;
        }
    }

    /**
     * Método para manejar logout
     */
    logout() {
        this.setAuthToken(null);
    }
}

/**
 * Clase personalizada para errores de API
 */
class ApiError extends Error {
    constructor(message, status = 500, details = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;
    }

    /**
     * Verificar si es un error de autenticación
     */
    isAuthError() {
        return this.status === 401;
    }

    /**
     * Verificar si es un error de validación
     */
    isValidationError() {
        return this.status === 400 || this.status === 422;
    }

    /**
     * Verificar si es un error del servidor
     */
    isServerError() {
        return this.status >= 500;
    }
}