/**
 * BaseModel - Clase base para todos los modelos
 * Maneja operaciones CRUD básicas y validaciones
 */
class BaseModel {
    constructor(data = {}) {
        this.id = data.id || null;
        this.createdAt = data.createdAt || new Date().toISOString();
        this.updatedAt = data.updatedAt || new Date().toISOString();
    }

    /**
     * Validar el modelo antes de guardar
     * @returns {Object} { isValid: boolean, errors: Array }
     */
    validate() {
        return { isValid: true, errors: [] };
    }

    /**
     * Convertir el modelo a objeto plano
     * @returns {Object}
     */
    toJSON() {
        const result = {};
        for (let key in this) {
            if (this.hasOwnProperty(key) && typeof this[key] !== 'function') {
                result[key] = this[key];
            }
        }
        return result;
    }

    /**
     * Actualizar propiedades del modelo
     * @param {Object} data 
     */
    update(data) {
        for (let key in data) {
            if (this.hasOwnProperty(key)) {
                this[key] = data[key];
            }
        }
        this.updatedAt = new Date().toISOString();
    }

    /**
     * Crear copia del modelo
     * @returns {BaseModel}
     */
    clone() {
        return new this.constructor(this.toJSON());
    }
}