/**
 * DateHelper - Utilidades para manejo de fechas
 * Centraliza todas las operaciones relacionadas con fechas
 */
class DateHelper {
    /**
     * Formatear fecha para display legible
     */
    static formatDate(dateInput, format = 'short') {
        if (!dateInput) return 'N/A';
        
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return 'Fecha inválida';

        const options = {
            short: {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            },
            long: {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            },
            medium: {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            },
            time: {
                hour: '2-digit',
                minute: '2-digit'
            },
            datetime: {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }
        };

        return date.toLocaleDateString('es-ES', options[format] || options.short);
    }

    /**
     * Formatear fecha relativa (ej: \"hace 2 días\", \"en 3 días\")
     */
    static formatRelativeDate(dateInput) {
        if (!dateInput) return 'N/A';
        
        const date = new Date(dateInput);
        const now = new Date();
        
        if (isNaN(date.getTime())) return 'Fecha inválida';

        const diffTime = date - now;
        const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.round(diffTime / (1000 * 60 * 60));
        const diffMinutes = Math.round(diffTime / (1000 * 60));

        // Fechas pasadas
        if (diffDays < -365) {
            const years = Math.floor(-diffDays / 365);
            return `Hace ${years} ${years === 1 ? 'año' : 'años'}`;
        } else if (diffDays < -30) {
            const months = Math.floor(-diffDays / 30);
            return `Hace ${months} ${months === 1 ? 'mes' : 'meses'}`;
        } else if (diffDays < -7) {
            const weeks = Math.floor(-diffDays / 7);
            return `Hace ${weeks} ${weeks === 1 ? 'semana' : 'semanas'}`;
        } else if (diffDays < -1) {
            return `Hace ${-diffDays} días`;
        } else if (diffDays === -1) {
            return 'Ayer';
        } else if (diffHours < -1) {
            return `Hace ${-diffHours} ${-diffHours === 1 ? 'hora' : 'horas'}`;
        } else if (diffMinutes < -1) {
            return `Hace ${-diffMinutes} ${-diffMinutes === 1 ? 'minuto' : 'minutos'}`;
        }
        
        // Fechas actuales
        if (diffDays === 0 && Math.abs(diffHours) < 1) {
            return 'Ahora';
        } else if (diffDays === 0) {
            return 'Hoy';
        }
        
        // Fechas futuras
        if (diffMinutes >= 1 && diffMinutes < 60) {
            return `En ${diffMinutes} ${diffMinutes === 1 ? 'minuto' : 'minutos'}`;
        } else if (diffHours >= 1 && diffHours < 24) {
            return `En ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
        } else if (diffDays === 1) {
            return 'Mañana';
        } else if (diffDays < 7) {
            return `En ${diffDays} días`;
        } else if (diffDays < 30) {
            const weeks = Math.floor(diffDays / 7);
            return `En ${weeks} ${weeks === 1 ? 'semana' : 'semanas'}`;
        } else if (diffDays < 365) {
            const months = Math.floor(diffDays / 30);
            return `En ${months} ${months === 1 ? 'mes' : 'meses'}`;
        } else {
            const years = Math.floor(diffDays / 365);
            return `En ${years} ${years === 1 ? 'año' : 'años'}`;
        }
    }

    /**
     * Obtener fecha en formato ISO para inputs
     */
    static toInputDate(dateInput) {
        if (!dateInput) return '';
        
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return '';

        return date.toISOString().split('T')[0];
    }

    /**
     * Obtener datetime en formato ISO para inputs datetime-local
     */
    static toInputDateTime(dateInput) {
        if (!dateInput) return '';
        
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return '';

        // Ajustar a timezone local
        const offsetMs = date.getTimezoneOffset() * 60 * 1000;
        const localTime = new Date(date.getTime() - offsetMs);
        
        return localTime.toISOString().slice(0, 16);
    }

    /**
     * Verificar si una fecha está vencida
     */
    static isOverdue(dateInput) {
        if (!dateInput) return false;
        
        const date = new Date(dateInput);
        const today = new Date();
        
        // Resetear la hora para comparar solo fechas
        today.setHours(23, 59, 59, 999);
        
        return date < today;
    }

    /**
     * Verificar si una fecha es hoy
     */
    static isToday(dateInput) {
        if (!dateInput) return false;
        
        const date = new Date(dateInput);
        const today = new Date();
        
        return date.toDateString() === today.toDateString();
    }

    /**
     * Verificar si una fecha es esta semana
     */
    static isThisWeek(dateInput) {
        if (!dateInput) return false;
        
        const date = new Date(dateInput);
        const today = new Date();
        
        // Obtener el inicio de la semana (lunes)
        const startOfWeek = new Date(today);
        const day = today.getDay();
        const diff = today.getDate() - day + (day === 0 ? -6 : 1);
        startOfWeek.setDate(diff);
        startOfWeek.setHours(0, 0, 0, 0);
        
        // Obtener el fin de la semana (domingo)
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        endOfWeek.setHours(23, 59, 59, 999);
        
        return date >= startOfWeek && date <= endOfWeek;
    }

    /**
     * Obtener días entre dos fechas
     */
    static daysBetween(startDate, endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (isNaN(start.getTime()) || isNaN(end.getTime())) return null;
        
        const diffTime = end - start;
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }

    /**
     * Agregar días a una fecha
     */
    static addDays(dateInput, days) {
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return null;
        
        date.setDate(date.getDate() + days);
        return date;
    }

    /**
     * Obtener inicio del día
     */
    static startOfDay(dateInput) {
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return null;
        
        date.setHours(0, 0, 0, 0);
        return date;
    }

    /**
     * Obtener fin del día
     */
    static endOfDay(dateInput) {
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return null;
        
        date.setHours(23, 59, 59, 999);
        return date;
    }

    /**
     * Obtener inicio de la semana
     */
    static startOfWeek(dateInput) {
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return null;
        
        const day = date.getDay();
        const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Lunes como inicio
        const monday = new Date(date.setDate(diff));
        monday.setHours(0, 0, 0, 0);
        
        return monday;
    }

    /**
     * Obtener fin de la semana
     */
    static endOfWeek(dateInput) {
        const startOfWeek = this.startOfWeek(dateInput);
        if (!startOfWeek) return null;
        
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        endOfWeek.setHours(23, 59, 59, 999);
        
        return endOfWeek;
    }

    /**
     * Obtener rango de fechas para filtros
     */
    static getDateRange(period) {
        const today = new Date();
        const ranges = {
            today: {
                start: this.startOfDay(today),
                end: this.endOfDay(today)
            },
            week: {
                start: this.startOfWeek(today),
                end: this.endOfWeek(today)
            },
            month: {
                start: new Date(today.getFullYear(), today.getMonth(), 1),
                end: new Date(today.getFullYear(), today.getMonth() + 1, 0, 23, 59, 59, 999)
            },
            quarter: {
                start: new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3, 1),
                end: new Date(today.getFullYear(), Math.floor(today.getMonth() / 3) * 3 + 3, 0, 23, 59, 59, 999)
            },
            year: {
                start: new Date(today.getFullYear(), 0, 1),
                end: new Date(today.getFullYear(), 11, 31, 23, 59, 59, 999)
            }
        };

        return ranges[period] || null;
    }

    /**
     * Formatear duración en texto legible
     */
    static formatDuration(startDate, endDate) {
        const days = this.daysBetween(startDate, endDate);
        if (days === null) return 'N/A';
        
        if (days === 0) return 'Mismo día';
        if (days === 1) return '1 día';
        if (days < 7) return `${days} días`;
        if (days < 30) {
            const weeks = Math.floor(days / 7);
            const remainingDays = days % 7;
            let result = `${weeks} ${weeks === 1 ? 'semana' : 'semanas'}`;
            if (remainingDays > 0) {
                result += ` y ${remainingDays} ${remainingDays === 1 ? 'día' : 'días'}`;
            }
            return result;
        }
        if (days < 365) {
            const months = Math.floor(days / 30);
            return `${months} ${months === 1 ? 'mes' : 'meses'}`;
        }
        
        const years = Math.floor(days / 365);
        const remainingMonths = Math.floor((days % 365) / 30);
        let result = `${years} ${years === 1 ? 'año' : 'años'}`;
        if (remainingMonths > 0) {
            result += ` y ${remainingMonths} ${remainingMonths === 1 ? 'mes' : 'meses'}`;
        }
        return result;
    }

    /**
     * Obtener nombre del día de la semana
     */
    static getDayName(dateInput, format = 'long') {
        if (!dateInput) return 'N/A';
        
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return 'N/A';

        const options = { weekday: format };
        return date.toLocaleDateString('es-ES', options);
    }

    /**
     * Obtener nombre del mes
     */
    static getMonthName(dateInput, format = 'long') {
        if (!dateInput) return 'N/A';
        
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return 'N/A';

        const options = { month: format };
        return date.toLocaleDateString('es-ES', options);
    }

    /**
     * Parsear fecha desde string flexible
     */
    static parseDate(dateString) {
        if (!dateString) return null;
        
        // Intentar diferentes formatos
        const formats = [
            // ISO format
            /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/,
            // ISO date only
            /^\d{4}-\d{2}-\d{2}$/,
            // DD/MM/YYYY
            /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/,
            // DD-MM-YYYY
            /^(\d{1,2})-(\d{1,2})-(\d{4})$/,
            // MM/DD/YYYY
            /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/
        ];

        // Intentar parseo directo primero
        let date = new Date(dateString);
        if (!isNaN(date.getTime())) {
            return date;
        }

        // Intentar formatos específicos
        const ddmmyyyyMatch = dateString.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
        if (ddmmyyyyMatch) {
            const [, day, month, year] = ddmmyyyyMatch;
            date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
            if (!isNaN(date.getTime())) {
                return date;
            }
        }

        return null;
    }

    /**
     * Obtener timestamp Unix
     */
    static toTimestamp(dateInput) {
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return null;
        
        return Math.floor(date.getTime() / 1000);
    }

    /**
     * Crear fecha desde timestamp Unix
     */
    static fromTimestamp(timestamp) {
        return new Date(timestamp * 1000);
    }

    /**
     * Verificar si es año bisiesto
     */
    static isLeapYear(year) {
        return ((year % 4 === 0) && (year % 100 !== 0)) || (year % 400 === 0);
    }

    /**
     * Obtener días en un mes
     */
    static getDaysInMonth(year, month) {
        return new Date(year, month, 0).getDate();
    }
}