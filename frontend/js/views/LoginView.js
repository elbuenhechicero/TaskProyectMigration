/**
 * LoginView - Vista de autenticación
 * Maneja el formulario de login y registro
 */
class LoginView extends BaseView {
    constructor() {
        super('loginContainer');
        this.isLoginMode = true;
    }

    /**
     * Renderizar vista de login
     */
    render() {
        if (!this.container) {
            console.error('Login container not found');
            return;
        }

        this.container.innerHTML = `
            <div class="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-800 flex items-center justify-center p-4">
                <div class="max-w-md w-full bg-white rounded-xl shadow-2xl overflow-hidden">
                    <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white text-center">
                        <i class="fas fa-tasks text-4xl mb-3"></i>
                        <h1 class="text-2xl font-bold">Task Manager</h1>
                        <p class="text-blue-100">Sistema de Gestión de Tareas</p>
                    </div>
                    
                    <div class="p-8">
                        <!-- Tabs -->
                        <div class="flex mb-6 bg-gray-100 rounded-lg p-1">
                            <button id="loginTab" class="flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200 bg-white text-blue-600 shadow-sm">
                                <i class="fas fa-sign-in-alt mr-2"></i>Iniciar Sesión
                            </button>
                            <button id="registerTab" class="flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200 text-gray-600 hover:text-blue-600">
                                <i class="fas fa-user-plus mr-2"></i>Registrarse
                            </button>
                        </div>

                        <!-- Login Form -->
                        <form id="loginForm" class="space-y-4">
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-user mr-2"></i>Usuario
                                    </label>
                                    <input 
                                        type="text" 
                                        id="loginUsername" 
                                        name="username"
                                        value="admin"
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Ingrese su usuario"
                                        required
                                    >
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-lock mr-2"></i>Contraseña
                                    </label>
                                    <div class="relative">
                                        <input 
                                            type="password" 
                                            id="loginPassword" 
                                            name="password"
                                            value="admin"
                                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                                            placeholder="Ingrese su contraseña"
                                            required
                                        >
                                        <button type="button" id="togglePassword" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <button 
                                type="submit" 
                                class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105"
                            >
                                <i class="fas fa-sign-in-alt mr-2"></i>Iniciar Sesión
                            </button>
                        </form>

                        <!-- Register Form -->
                        <form id="registerForm" class="space-y-4 hidden">
                            <div class="space-y-4">
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Nombre</label>
                                        <input 
                                            type="text" 
                                            id="registerFirstName"
                                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="Nombre"
                                            required
                                        >
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Apellido</label>
                                        <input 
                                            type="text" 
                                            id="registerLastName"
                                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                            placeholder="Apellido"
                                            required
                                        >
                                    </div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-user mr-2"></i>Usuario
                                    </label>
                                    <input 
                                        type="text" 
                                        id="registerUsername"
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Nombre de usuario"
                                        required
                                    >
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-envelope mr-2"></i>Email
                                    </label>
                                    <input 
                                        type="email" 
                                        id="registerEmail"
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="correo@ejemplo.com"
                                        required
                                    >
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-lock mr-2"></i>Contraseña
                                    </label>
                                    <input 
                                        type="password" 
                                        id="registerPassword"
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Contraseña"
                                        required
                                    >
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-2">
                                        <i class="fas fa-lock mr-2"></i>Confirmar Contraseña
                                    </label>
                                    <input 
                                        type="password" 
                                        id="registerConfirmPassword"
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Confirmar contraseña"
                                        required
                                    >
                                </div>
                            </div>
                            
                            <button 
                                type="submit" 
                                class="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-3 rounded-lg font-medium hover:from-green-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105"
                            >
                                <i class="fas fa-user-plus mr-2"></i>Registrarse
                            </button>
                        </form>

                        <!-- Demo Users Info -->
                        <div class="mt-6 p-4 bg-blue-50 rounded-lg">
                            <h4 class="text-sm font-medium text-blue-800 mb-2">
                                <i class="fas fa-info-circle mr-1"></i>Usuarios de Prueba
                            </h4>
                            <div class="text-xs text-blue-600 space-y-1">
                                <div><strong>admin/admin</strong> - Administrador</div>
                                <div><strong>user1/user1</strong> - Usuario estándar</div>
                                <div><strong>user2/user2</strong> - Usuario estándar</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Adjuntar event listeners
     */
    attachEventListeners() {
        // Tab switching
        const loginTab = this.container.querySelector('#loginTab');
        const registerTab = this.container.querySelector('#registerTab');
        const loginForm = this.container.querySelector('#loginForm');
        const registerForm = this.container.querySelector('#registerForm');

        loginTab.onclick = () => this.switchTab('login', loginTab, registerTab, loginForm, registerForm);
        registerTab.onclick = () => this.switchTab('register', registerTab, loginTab, registerForm, loginForm);

        // Password toggle
        const togglePassword = this.container.querySelector('#togglePassword');
        const passwordInput = this.container.querySelector('#loginPassword');
        
        togglePassword.onclick = () => {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePassword.innerHTML = type === 'password' ? '<i class=\"fas fa-eye\"></i>' : '<i class=\"fas fa-eye-slash\"></i>';
        };

        // Form submissions
        loginForm.onsubmit = (e) => this.handleLogin(e);
        registerForm.onsubmit = (e) => this.handleRegister(e);
    }

    /**
     * Cambiar entre tabs de login y registro
     */
    switchTab(mode, activeTab, inactiveTab, activeForm, inactiveForm) {
        this.isLoginMode = mode === 'login';

        // Update tab styles
        activeTab.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200 bg-white text-blue-600 shadow-sm';
        inactiveTab.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all duration-200 text-gray-600 hover:text-blue-600';

        // Show/hide forms
        activeForm.classList.remove('hidden');
        inactiveForm.classList.add('hidden');

        // Clear any existing error messages
        const errorMessages = this.container.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());
    }

    /**
     * Manejar submit de login
     */
    async handleLogin(event) {
        event.preventDefault();
        
        const username = this.container.querySelector('#loginUsername').value;
        const password = this.container.querySelector('#loginPassword').value;
        const submitBtn = this.container.querySelector('#loginForm button[type=\"submit\"]');
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class=\"fas fa-spinner fa-spin mr-2\"></i>Iniciando sesión...';
        submitBtn.disabled = true;

        try {
            // Emitir evento personalizado para el controlador
            const loginEvent = new CustomEvent('loginAttempt', {
                detail: { username, password }
            });
            document.dispatchEvent(loginEvent);

        } catch (error) {
            this.showError(error.message || 'Error al iniciar sesión');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Manejar submit de registro
     */
    async handleRegister(event) {
        event.preventDefault();
        
        const formData = {
            username: this.container.querySelector('#registerUsername').value,
            email: this.container.querySelector('#registerEmail').value,
            password: this.container.querySelector('#registerPassword').value,
            confirmPassword: this.container.querySelector('#registerConfirmPassword').value,
            profile: {
                firstName: this.container.querySelector('#registerFirstName').value,
                lastName: this.container.querySelector('#registerLastName').value
            }
        };
        
        // Validar contraseñas
        if (formData.password !== formData.confirmPassword) {
            this.showError('Las contraseñas no coinciden');
            return;
        }
        
        const submitBtn = this.container.querySelector('#registerForm button[type=\"submit\"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class=\"fas fa-spinner fa-spin mr-2\"></i>Registrando...';
        submitBtn.disabled = true;

        try {
            // Emitir evento personalizado para el controlador
            const registerEvent = new CustomEvent('registerAttempt', {
                detail: formData
            });
            document.dispatchEvent(registerEvent);

        } catch (error) {
            this.showError(error.message || 'Error al registrarse');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Mostrar mensaje de éxito de login
     */
    showLoginSuccess() {
        this.showSuccess('¡Bienvenido! Iniciando sesión...');
    }

    /**
     * Mostrar mensaje de éxito de registro
     */
    showRegisterSuccess() {
        this.showSuccess('¡Registro exitoso! Iniciando sesión...');
    }
}