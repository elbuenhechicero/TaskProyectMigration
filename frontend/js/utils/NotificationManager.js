/**
 * NotificationManager - Manejo de notificaciones toast
 * Sistema unificado para mostrar mensajes al usuario
 */
class NotificationManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        this.notifications = [];
        this.maxNotifications = 5;
        
        if (!this.container) {
            this.createContainer();
        }
    }

    /**
     * Crear contenedor de notificaciones si no existe
     */
    createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'toastContainer';
        this.container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(this.container);
    }

    /**
     * Mostrar notificación
     */
    show(message, type = 'info', duration = 5000, options = {}) {
        const notification = {
            id: Date.now() + Math.random(),
            message,
            type,
            duration,
            ...options
        };

        // Limitar número de notificaciones
        if (this.notifications.length >= this.maxNotifications) {
            this.remove(this.notifications[0].id);
        }

        this.notifications.push(notification);
        this.render(notification);

        // Auto-remover después de la duración especificada
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification.id);
            }, duration);
        }

        return notification.id;
    }

    /**
     * Mostrar notificación de éxito
     */
    success(message, duration = 3000, options = {}) {
        return this.show(message, 'success', duration, {
            icon: 'fas fa-check-circle',
            ...options
        });
    }

    /**
     * Mostrar notificación de error
     */
    error(message, duration = 7000, options = {}) {
        return this.show(message, 'error', duration, {
            icon: 'fas fa-exclamation-circle',
            ...options
        });
    }

    /**
     * Mostrar notificación de advertencia
     */
    warning(message, duration = 5000, options = {}) {
        return this.show(message, 'warning', duration, {
            icon: 'fas fa-exclamation-triangle',
            ...options
        });
    }

    /**
     * Mostrar notificación informativa
     */
    info(message, duration = 4000, options = {}) {
        return this.show(message, 'info', duration, {
            icon: 'fas fa-info-circle',
            ...options
        });
    }

    /**
     * Renderizar notificación individual
     */
    render(notification) {
        const toastElement = document.createElement('div');
        toastElement.id = `toast-${notification.id}`;
        toastElement.className = this.getToastClasses(notification.type);
        
        toastElement.innerHTML = `
            <div class="flex items-center p-4 rounded-lg shadow-lg max-w-sm w-full">
                ${notification.icon ? `<i class="${notification.icon} mr-3 text-lg"></i>` : ''}
                <div class="flex-1">
                    ${notification.title ? `<h4 class="font-semibold mb-1">${notification.title}</h4>` : ''}
                    <p class="text-sm ${notification.title ? 'opacity-90' : ''}">${notification.message}</p>
                </div>
                ${!notification.persistent ? `
                    <button class="ml-3 text-current opacity-70 hover:opacity-100 transition-opacity" onclick="notificationManager.remove(${notification.id})">
                        <i class="fas fa-times"></i>
                    </button>
                ` : ''}
            </div>
        `;

        // Animación de entrada
        toastElement.style.transform = 'translateX(100%)';
        toastElement.style.opacity = '0';
        
        this.container.appendChild(toastElement);
        
        // Trigger animation
        requestAnimationFrame(() => {
            toastElement.style.transition = 'all 0.3s ease-in-out';
            toastElement.style.transform = 'translateX(0)';
            toastElement.style.opacity = '1';
        });

        // Agregar eventos
        if (notification.onClick) {
            toastElement.style.cursor = 'pointer';
            toastElement.onclick = notification.onClick;
        }

        // Auto-dismiss on hover pause
        if (notification.pauseOnHover && notification.duration > 0) {
            let remainingTime = notification.duration;
            let startTime = Date.now();
            let timeoutId;

            const scheduleRemoval = () => {
                timeoutId = setTimeout(() => {
                    this.remove(notification.id);
                }, remainingTime);
            };

            toastElement.onmouseenter = () => {
                clearTimeout(timeoutId);
                remainingTime -= (Date.now() - startTime);
            };

            toastElement.onmouseleave = () => {
                startTime = Date.now();
                scheduleRemoval();
            };
        }
    }

    /**
     * Obtener clases CSS para el tipo de toast
     */
    getToastClasses(type) {
        const baseClasses = 'toast transform transition-all duration-300 ease-in-out';
        
        const typeClasses = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };

        return `${baseClasses} ${typeClasses[type] || typeClasses.info}`;
    }

    /**
     * Remover notificación
     */
    remove(notificationId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        const element = document.getElementById(`toast-${notificationId}`);
        
        if (element) {
            // Animación de salida
            element.style.transform = 'translateX(100%)';
            element.style.opacity = '0';
            
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            }, 300);
        }

        // Remover de la lista
        this.notifications = this.notifications.filter(n => n.id !== notificationId);
    }

    /**
     * Limpiar todas las notificaciones
     */
    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification.id);
        });
        this.notifications = [];
    }

    /**
     * Mostrar notificación de progreso
     */
    showProgress(message, progress = 0, options = {}) {
        const id = this.show(message, 'info', 0, {
            persistent: true,
            icon: 'fas fa-spinner fa-spin',
            progress: true,
            ...options
        });

        this.updateProgress(id, progress);
        return id;
    }

    /**
     * Actualizar progreso de una notificación
     */
    updateProgress(notificationId, progress) {
        const element = document.getElementById(`toast-${notificationId}`);
        if (element) {
            let progressBar = element.querySelector('.progress-bar');
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'progress-bar w-full bg-white bg-opacity-30 rounded-full h-1 mt-2';
                progressBar.innerHTML = '<div class="progress-fill bg-white h-full rounded-full transition-all duration-300" style="width: 0%"></div>';
                element.querySelector('.flex-1').appendChild(progressBar);
            }
            
            const fill = progressBar.querySelector('.progress-fill');
            if (fill) {
                fill.style.width = `${Math.min(100, Math.max(0, progress))}%`;
            }
        }
    }

    /**
     * Completar notificación de progreso
     */
    completeProgress(notificationId, message = 'Completado', autoRemove = true) {
        const element = document.getElementById(`toast-${notificationId}`);
        if (element) {
            // Cambiar icono y mensaje
            const icon = element.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-check-circle mr-3 text-lg';
            }
            
            const messageEl = element.querySelector('.flex-1 p');
            if (messageEl) {
                messageEl.textContent = message;
            }

            // Actualizar progreso al 100%
            this.updateProgress(notificationId, 100);

            if (autoRemove) {
                setTimeout(() => {
                    this.remove(notificationId);
                }, 2000);
            }
        }
    }

    /**
     * Mostrar confirmación con acciones
     */
    showConfirmation(message, onConfirm, onCancel = null, options = {}) {
        const id = this.show(message, 'warning', 0, {
            persistent: true,
            icon: 'fas fa-question-circle',
            title: options.title || 'Confirmación requerida',
            actions: true,
            ...options
        });

        // Agregar botones de acción
        const element = document.getElementById(`toast-${id}`);
        if (element) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'flex space-x-2 mt-3';
            
            actionsDiv.innerHTML = `
                <button class="confirm-btn bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded text-sm transition-all">
                    ${options.confirmText || 'Confirmar'}
                </button>
                <button class="cancel-btn bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded text-sm transition-all">
                    ${options.cancelText || 'Cancelar'}
                </button>
            `;
            
            const flexDiv = element.querySelector('.flex-1');
            flexDiv.appendChild(actionsDiv);
            
            // Event listeners
            actionsDiv.querySelector('.confirm-btn').onclick = (e) => {
                e.stopPropagation();
                this.remove(id);
                if (onConfirm) onConfirm();
            };
            
            actionsDiv.querySelector('.cancel-btn').onclick = (e) => {
                e.stopPropagation();
                this.remove(id);
                if (onCancel) onCancel();
            };
        }

        return id;
    }
}

// Crear instancia global
const notificationManager = new NotificationManager();

// Hacer disponible globalmente
window.notificationManager = notificationManager;