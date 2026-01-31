/**
 * ValidationHelper - Utilidades para validación de formularios
 * Centraliza todas las validaciones comunes de la aplicación
 */
class ValidationHelper {
    /**
     * Validar email
     */
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Validar contraseña
     */
    static isValidPassword(password, minLength = 4) {
        return password && password.length >= minLength;
    }

    /**
     * Validar nombre de usuario
     */
    static isValidUsername(username, minLength = 3, maxLength = 20) {
        if (!username) return false;
        const usernameRegex = /^[a-zA-Z0-9_.-]+$/;
        return username.length >= minLength && 
               username.length <= maxLength && 
               usernameRegex.test(username);
    }

    /**
     * Validar fecha
     */
    static isValidDate(dateString) {
        if (!dateString) return false;
        const date = new Date(dateString);
        return !isNaN(date.getTime());
    }

    /**
     * Validar fecha futura
     */
    static isFutureDate(dateString) {
        if (!this.isValidDate(dateString)) return false;
        const date = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Reset time to compare only dates
        return date >= today;
    }

    /**
     * Validar rango de fechas
     */
    static isValidDateRange(startDate, endDate) {
        if (!this.isValidDate(startDate) || !this.isValidDate(endDate)) {
            return false;
        }
        return new Date(startDate) <= new Date(endDate);
    }

    /**
     * Validar número positivo
     */
    static isPositiveNumber(value) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= 0;
    }

    /**
     * Validar rango numérico
     */
    static isInRange(value, min, max) {
        const num = parseFloat(value);
        if (isNaN(num)) return false;
        return num >= min && num <= max;
    }

    /**
     * Validar longitud de texto
     */
    static isValidLength(text, minLength = 0, maxLength = Infinity) {
        if (!text) return minLength === 0;
        return text.length >= minLength && text.length <= maxLength;
    }

    /**
     * Validar que el texto no esté vacío
     */
    static isNotEmpty(text) {
        return text && text.trim().length > 0;
    }

    /**
     * Validar URL
     */
    static isValidURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    /**
     * Validar número de teléfono (formato básico)
     */
    static isValidPhone(phone) {
        const phoneRegex = /^\+?[\d\s\-\(\)]{7,15}$/;
        return phoneRegex.test(phone);
    }

    /**
     * Validar formulario completo
     */
    static validateForm(formData, rules) {
        const errors = {};
        
        for (const [field, rule] of Object.entries(rules)) {
            const value = formData[field];
            const fieldErrors = [];

            // Validación requerida
            if (rule.required && !this.isNotEmpty(value)) {
                fieldErrors.push(rule.requiredMessage || `${field} es obligatorio`);
                continue; // Skip other validations if required field is empty
            }

            // Skip other validations if field is empty and not required
            if (!this.isNotEmpty(value) && !rule.required) {
                continue;
            }

            // Validación de longitud
            if (rule.minLength !== undefined || rule.maxLength !== undefined) {
                const min = rule.minLength || 0;
                const max = rule.maxLength || Infinity;
                if (!this.isValidLength(value, min, max)) {
                    fieldErrors.push(rule.lengthMessage || `${field} debe tener entre ${min} y ${max} caracteres`);
                }
            }

            // Validación de email
            if (rule.email && !this.isValidEmail(value)) {
                fieldErrors.push(rule.emailMessage || `${field} debe ser un email válido`);
            }

            // Validación de contraseña
            if (rule.password) {
                const minLength = rule.passwordMinLength || 4;
                if (!this.isValidPassword(value, minLength)) {
                    fieldErrors.push(rule.passwordMessage || `${field} debe tener al menos ${minLength} caracteres`);
                }
            }

            // Validación de nombre de usuario
            if (rule.username && !this.isValidUsername(value)) {
                fieldErrors.push(rule.usernameMessage || `${field} debe contener solo letras, números, guiones y puntos`);
            }

            // Validación de fecha
            if (rule.date && !this.isValidDate(value)) {
                fieldErrors.push(rule.dateMessage || `${field} debe ser una fecha válida`);
            }

            // Validación de fecha futura
            if (rule.futureDate && !this.isFutureDate(value)) {
                fieldErrors.push(rule.futureDateMessage || `${field} debe ser una fecha futura`);
            }

            // Validación numérica
            if (rule.number && !this.isPositiveNumber(value)) {
                fieldErrors.push(rule.numberMessage || `${field} debe ser un número válido`);
            }

            // Validación de rango numérico
            if (rule.range) {
                if (!this.isInRange(value, rule.range.min, rule.range.max)) {
                    fieldErrors.push(rule.rangeMessage || `${field} debe estar entre ${rule.range.min} y ${rule.range.max}`);
                }
            }

            // Validación personalizada
            if (rule.custom && typeof rule.custom === 'function') {
                const customResult = rule.custom(value, formData);
                if (customResult !== true) {
                    fieldErrors.push(customResult || `${field} no es válido`);
                }
            }

            // Validación de coincidencia (para confirmación de contraseña)
            if (rule.matches) {
                const matchField = formData[rule.matches];
                if (value !== matchField) {
                    fieldErrors.push(rule.matchMessage || `${field} no coincide`);
                }
            }

            if (fieldErrors.length > 0) {
                errors[field] = fieldErrors;
            }
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }

    /**
     * Sanitizar entrada de texto
     */
    static sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        return input
            .trim()
            .replace(/[<>]/g, '') // Remove basic HTML tags
            .replace(/javascript:/gi, '') // Remove javascript: URLs
            .replace(/on\w+\s*=/gi, ''); // Remove event handlers
    }

    /**
     * Escapar HTML
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Validar archivo
     */
    static validateFile(file, options = {}) {
        const errors = [];
        
        if (!file) {
            if (options.required) {
                errors.push('Archivo es obligatorio');
            }
            return { isValid: errors.length === 0, errors };
        }

        // Validar tamaño
        if (options.maxSize && file.size > options.maxSize) {
            errors.push(`El archivo no puede superar ${this.formatFileSize(options.maxSize)}`);
        }

        // Validar tipo
        if (options.allowedTypes && !options.allowedTypes.includes(file.type)) {
            errors.push(`Tipo de archivo no permitido. Tipos permitidos: ${options.allowedTypes.join(', ')}`);
        }

        // Validar extensión
        if (options.allowedExtensions) {
            const extension = file.name.split('.').pop().toLowerCase();
            if (!options.allowedExtensions.includes(extension)) {
                errors.push(`Extensión no permitida. Extensiones permitidas: ${options.allowedExtensions.join(', ')}`);
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Formatear tamaño de archivo
     */
    static formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Mostrar errores en el formulario
     */
    static displayErrors(errors, formElement) {
        // Limpiar errores anteriores
        const existingErrors = formElement.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());

        // Mostrar nuevos errores
        for (const [field, fieldErrors] of Object.entries(errors)) {
            const fieldElement = formElement.querySelector(`[name="${field}"], #${field}`);
            
            if (fieldElement) {
                // Agregar clase de error al campo
                fieldElement.classList.add('border-red-500', 'focus:ring-red-500');
                fieldElement.classList.remove('border-gray-300', 'focus:ring-blue-500');

                // Crear y mostrar mensaje de error
                const errorDiv = document.createElement('div');
                errorDiv.className = 'validation-error text-red-500 text-sm mt-1';
                errorDiv.innerHTML = fieldErrors.map(error => 
                    `<div class="flex items-center"><i class="fas fa-exclamation-circle mr-1"></i>${error}</div>`
                ).join('');

                fieldElement.parentNode.appendChild(errorDiv);
            }
        }
    }

    /**
     * Limpiar errores del formulario
     */
    static clearErrors(formElement) {
        const existingErrors = formElement.querySelectorAll('.validation-error');
        existingErrors.forEach(error => error.remove());

        const errorFields = formElement.querySelectorAll('.border-red-500');
        errorFields.forEach(field => {
            field.classList.remove('border-red-500', 'focus:ring-red-500');
            field.classList.add('border-gray-300', 'focus:ring-blue-500');
        });
    }

    /**
     * Configurar validación en tiempo real
     */
    static setupRealTimeValidation(formElement, rules) {
        for (const [fieldName, rule] of Object.entries(rules)) {
            const field = formElement.querySelector(`[name="${fieldName}"], #${fieldName}`);
            
            if (field) {
                field.addEventListener('blur', () => {
                    const value = field.value;
                    const fieldValidation = this.validateForm({ [fieldName]: value }, { [fieldName]: rule });
                    
                    if (!fieldValidation.isValid) {
                        this.displayErrors(fieldValidation.errors, formElement);
                    } else {
                        // Limpiar errores de este campo específico
                        const existingError = field.parentNode.querySelector('.validation-error');
                        if (existingError) {
                            existingError.remove();
                            field.classList.remove('border-red-500', 'focus:ring-red-500');
                            field.classList.add('border-gray-300', 'focus:ring-blue-500');
                        }
                    }
                });
            }
        }
    }
}