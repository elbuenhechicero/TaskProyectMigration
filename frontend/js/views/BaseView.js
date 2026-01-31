/**
 * BaseView - Clase base para todas las vistas
 * Maneja operaciones comunes del DOM y eventos
 */
class BaseView {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.eventListeners = [];
    }

    /**
     * Renderizar la vista
     */
    render() {
        throw new Error('El método render() debe ser implementado por la clase hija');
    }

    /**
     * Mostrar la vista
     */
    show() {
        if (this.container) {
            this.container.classList.remove('hidden');
            this.container.style.display = 'block';
        }
    }

    /**
     * Ocultar la vista
     */
    hide() {
        if (this.container) {
            this.container.classList.add('hidden');
            this.container.style.display = 'none';
        }
    }

    /**
     * Crear elemento HTML
     */
    createElement(tag, className = '', content = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (content) element.innerHTML = content;
        return element;
    }

    /**
     * Agregar event listener y mantener referencia para limpieza
     */
    addEventListener(element, event, handler) {
        element.addEventListener(event, handler);
        this.eventListeners.push({ element, event, handler });
    }

    /**
     * Limpiar todos los event listeners
     */
    cleanup() {
        this.eventListeners.forEach(({ element, event, handler }) => {
            element.removeEventListener(event, handler);
        });
        this.eventListeners = [];
    }

    /**
     * Mostrar mensaje de error
     */
    showError(message, container = null) {
        const errorDiv = this.createElement('div', 'error-message bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4', 
            `<i class=\"fas fa-exclamation-triangle\"></i> ${message}`
        );
        
        const target = container || this.container;
        if (target) {
            // Remover errores anteriores
            const existingErrors = target.querySelectorAll('.error-message');
            existingErrors.forEach(error => error.remove());
            
            target.insertBefore(errorDiv, target.firstChild);
            
            // Auto-remover después de 5 segundos
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 5000);
        }
    }

    /**
     * Mostrar mensaje de éxito
     */
    showSuccess(message, container = null) {
        const successDiv = this.createElement('div', 'success-message bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4',
            `<i class=\"fas fa-check-circle\"></i> ${message}`
        );
        
        const target = container || this.container;
        if (target) {
            // Remover mensajes anteriores
            const existingMessages = target.querySelectorAll('.success-message');
            existingMessages.forEach(msg => msg.remove());
            
            target.insertBefore(successDiv, target.firstChild);
            
            // Auto-remover después de 3 segundos
            setTimeout(() => {
                if (successDiv.parentNode) {
                    successDiv.remove();
                }
            }, 3000);
        }
    }

    /**
     * Mostrar loading spinner
     */
    showLoading(container = null) {
        const loadingDiv = this.createElement('div', 'loading-spinner flex items-center justify-center p-4',
            `<i class=\"fas fa-spinner fa-spin mr-2\"></i> Cargando...`
        );
        
        const target = container || this.container;
        if (target) {
            target.appendChild(loadingDiv);
        }
        return loadingDiv;
    }

    /**
     * Ocultar loading spinner
     */
    hideLoading(container = null) {
        const target = container || this.container;
        if (target) {
            const spinner = target.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }
    }

    /**
     * Formatear fecha para display
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    /**
     * Formatear fecha relativa (ej: \"hace 2 días\")
     */
    formatRelativeDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = now - date;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Hoy';
        if (diffDays === 1) return 'Ayer';
        if (diffDays < 7) return `Hace ${diffDays} días`;
        if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
        return this.formatDate(dateString);
    }

    /**
     * Escapar HTML para prevenir XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Truncar texto con elipsis
     */
    truncateText(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Mostrar modal de confirmación
     */
    showConfirm(message, onConfirm, onCancel = null) {
        const modal = this.createElement('div', 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center');
        
        modal.innerHTML = `
            <div class=\"bg-white rounded-lg p-6 max-w-sm w-full mx-4\">
                <div class=\"text-center\">
                    <i class=\"fas fa-question-circle text-4xl text-yellow-500 mb-4\"></i>
                    <h3 class=\"text-lg font-semibold mb-4\">${message}</h3>
                    <div class=\"flex justify-center space-x-4\">
                        <button class=\"confirm-btn bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded\">
                            Confirmar
                        </button>
                        <button class=\"cancel-btn bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded\">
                            Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        const confirmBtn = modal.querySelector('.confirm-btn');
        const cancelBtn = modal.querySelector('.cancel-btn');
        
        confirmBtn.onclick = () => {
            document.body.removeChild(modal);
            if (onConfirm) onConfirm();
        };
        
        cancelBtn.onclick = () => {
            document.body.removeChild(modal);
            if (onCancel) onCancel();
        };
        
        // Cerrar al hacer click fuera del modal
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                if (onCancel) onCancel();
            }
        };
        
        document.body.appendChild(modal);
    }
}