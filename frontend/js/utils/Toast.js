/**
 * NotificationManager - Sistema de notificaciones toast
 * Maneja notificaciones temporales y permanentes
 */
class NotificationManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        this.notifications = [];
        this.defaultDuration = 5000; // 5 segundos
        
        this.init();
    }

    /**
     * Inicializar el sistema de notificaciones
     */
    init() {
        if (!this.container) {
            this.createContainer();
        }
    }

    /**
     * Crear contenedor si no existe
     */
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'toastContainer';
        this.container.className = 'fixed top-4 right-4 z-50 space-y-2 max-w-sm';
        document.body.appendChild(this.container);
    }

    /**
     * Mostrar notificación de éxito
     */
    success(message, options = {}) {
        return this.show({
            type: 'success',
            title: options.title || '¡Éxito!',
            message,
            icon: 'fas fa-check-circle',
            duration: options.duration || this.defaultDuration,
            persistent: options.persistent || false
        });
    }

    /**
     * Mostrar notificación de error
     */
    error(message, options = {}) {
        return this.show({
            type: 'error',
            title: options.title || 'Error',
            message,
            icon: 'fas fa-exclamation-circle',
            duration: options.duration || this.defaultDuration * 2, // Errores duran más
            persistent: options.persistent || false
        });
    }

    /**
     * Mostrar notificación de advertencia
     */
    warning(message, options = {}) {
        return this.show({
            type: 'warning',
            title: options.title || 'Advertencia',
            message,
            icon: 'fas fa-exclamation-triangle',
            duration: options.duration || this.defaultDuration,
            persistent: options.persistent || false
        });
    }

    /**
     * Mostrar notificación informativa
     */
    info(message, options = {}) {
        return this.show({
            type: 'info',
            title: options.title || 'Información',
            message,
            icon: 'fas fa-info-circle',
            duration: options.duration || this.defaultDuration,
            persistent: options.persistent || false
        });
    }

    /**
     * Mostrar notificación personalizada
     */
    show(config) {
        const notification = this.createNotification(config);
        this.notifications.push(notification);
        
        // Agregar al DOM con animación
        this.container.appendChild(notification.element);
        
        // Trigger animation
        requestAnimationFrame(() => {
            notification.element.classList.remove('toast-enter');
            notification.element.classList.add('toast-enter-active');
        });

        // Auto-cerrar si no es persistente
        if (config.duration > 0 && !config.persistent) {
            notification.timeout = setTimeout(() => {
                this.remove(notification.id);
            }, config.duration);
        }

        return notification.id;
    }

    /**
     * Crear elemento de notificación
     */
    createNotification(config) {
        const id = 'notification_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        
        const element = document.createElement('div');
        element.id = id;
        element.className = `toast toast-${config.type} toast-enter bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm transform transition-all duration-300`;
        
        // Determinar colores según el tipo
        const typeStyles = {
            success: 'border-green-200 bg-green-50',
            error: 'border-red-200 bg-red-50',
            warning: 'border-yellow-200 bg-yellow-50',
            info: 'border-blue-200 bg-blue-50'
        };

        const iconColors = {
            success: 'text-green-600',
            error: 'text-red-600',
            warning: 'text-yellow-600',
            info: 'text-blue-600'
        };

        element.className += ` ${typeStyles[config.type] || typeStyles.info}`;

        element.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    <i class="${config.icon} ${iconColors[config.type]} text-lg"></i>
                </div>
                <div class="ml-3 flex-1">
                    <h4 class="text-sm font-medium text-gray-900">
                        ${this.escapeHtml(config.title)}
                    </h4>
                    <p class="mt-1 text-sm text-gray-600">
                        ${this.escapeHtml(config.message)}
                    </p>
                </div>
                <div class="ml-4 flex-shrink-0">
                    <button class="close-notification bg-transparent rounded-md text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500" data-id="${id}">
                        <span class="sr-only">Cerrar</span>
                        <i class="fas fa-times text-sm"></i>
                    </button>
                </div>
            </div>
        `;

        // Agregar event listeners
        this.attachNotificationEvents(element, id);

        return {
            id,
            element,
            config,
            timeout: null
        };
    }

    /**
     * Adjuntar eventos a notificación
     */
    attachNotificationEvents(element, notificationId) {
        // Botón de cerrar
        const closeBtn = element.querySelector('.close-notification');
        if (closeBtn) {
            closeBtn.onclick = () => this.remove(notificationId);
        }

        // Pausar auto-close en hover
        element.onmouseenter = () => {
            const notification = this.notifications.find(n => n.id === notificationId);
            if (notification && notification.timeout) {
                clearTimeout(notification.timeout);
                notification.timeout = null;
            }
        };

        // Reanudar auto-close al salir del hover
        element.onmouseleave = () => {
            const notification = this.notifications.find(n => n.id === notificationId);
            if (notification && notification.config.duration > 0 && !notification.config.persistent) {
                notification.timeout = setTimeout(() => {
                    this.remove(notificationId);
                }, 1000);
            }
        };
    }

    /**
     * Remover notificación
     */
    remove(notificationId) {
        const notificationIndex = this.notifications.findIndex(n => n.id === notificationId);
        if (notificationIndex === -1) return;

        const notification = this.notifications[notificationIndex];
        
        // Limpiar timeout si existe
        if (notification.timeout) {
            clearTimeout(notification.timeout);
        }

        // Animación de salida
        notification.element.classList.remove('toast-enter-active');
        notification.element.classList.add('toast-exit', 'toast-exit-active');

        // Remover del DOM después de la animación
        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
        }, 300);

        // Remover de la lista
        this.notifications.splice(notificationIndex, 1);
    }

    /**
     * Remover todas las notificaciones
     */
    clearAll() {
        this.notifications.forEach(notification => {
            this.remove(notification.id);
        });
    }

    /**
     * Escapar HTML para prevenir XSS
     */
    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Notificaciones predefinidas
    formSuccess(message = 'Datos guardados exitosamente') {
        return this.success(message, { duration: 3000 });
    }

    formError(message = 'Error al procesar el formulario') {
        return this.error(message, { duration: 6000 });
    }

    networkError() {
        return this.error('Error de conexión. Verifique su conexión a internet.', {
            title: 'Sin conexión',
            persistent: true
        });
    }
}

// Crear instancia global
window.notifications = new NotificationManager();