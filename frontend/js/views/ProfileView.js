/**
 * ProfileView - Vista para el perfil de usuario
 */
class ProfileView extends BaseView {
    constructor(authService) {
        super('pageContent');
        this.authService = authService;
        this.currentUser = null;
        this.activeTab = 'profile';
    }

    /**
     * Renderizar vista de perfil
     */
    async render(options = {}) {
        if (!this.container) {
            console.error('Profile container not found');
            return;
        }

        try {
            await this.loadUserData();
            this.container.innerHTML = this.getProfileTemplate();
            this.setupEventListeners();

        } catch (error) {
            console.error('Error loading profile:', error);
            this.showError('Error al cargar el perfil');
        }
    }

    /**
     * Cargar datos de usuario
     */
    async loadUserData() {
        try {
            this.currentUser = await this.authService.loadCurrentUser();
            if (!this.currentUser) {
                throw new Error('User not authenticated');
            }

        } catch (error) {
            console.warn('Could not load user data:', error);
            this.currentUser = {
                id: 1,
                username: 'usuario',
                email: 'usuario@example.com',
                firstName: 'Usuario',
                lastName: 'Ejemplo',
                avatar: 'https://via.placeholder.com/150',
                phone: '+34 600 000 000',
                joinDate: new Date('2024-01-15'),
                role: 'user',
                bio: 'Soy un usuario de prueba'
            };
        }
    }

    /**
     * Template principal de perfil
     */
    getProfileTemplate() {
        return `
            <div class="profile-container">
                <!-- Header de perfil -->
                <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg mb-6 p-8">
                    <div class="flex items-center">
                        <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center mr-6 shadow-lg">
                            <i class="fas fa-user text-4xl text-blue-600"></i>
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold">
                                ${this.currentUser.firstName} ${this.currentUser.lastName}
                            </h1>
                            <p class="text-blue-100">@${this.currentUser.username}</p>
                            <p class="text-blue-100 mt-2">
                                <i class="fas fa-user-tag mr-2"></i>
                                ${this.capitalize(this.currentUser.role)}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Tabs -->
                <div class="mb-6 border-b border-gray-200">
                    <div class="flex space-x-1">
                        <button class="profile-tab active px-6 py-3 font-medium text-gray-700 border-b-2 border-blue-600" data-tab="profile">
                            <i class="fas fa-user mr-2"></i>Perfil
                        </button>
                        <button class="profile-tab px-6 py-3 font-medium text-gray-700" data-tab="settings">
                            <i class="fas fa-cog mr-2"></i>Configuración
                        </button>
                        <button class="profile-tab px-6 py-3 font-medium text-gray-700" data-tab="security">
                            <i class="fas fa-lock mr-2"></i>Seguridad
                        </button>
                    </div>
                </div>

                <!-- Contenido de tabs -->
                <div id="profileContent">
                    ${this.getProfileTabContent()}
                </div>
            </div>
        `;
    }

    /**
     * Contenido del tab de perfil
     */
    getProfileTabContent() {
        return `
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Información general -->
                <div class="lg:col-span-2">
                    <div class="card mb-6">
                        <div class="card-header">
                            <h2 class="text-xl font-bold text-gray-900">Información General</h2>
                        </div>
                        <div class="card-body">
                            <form id="profileForm" class="space-y-4">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                                        <input type="text" id="firstName" value="${this.currentUser.firstName}" class="form-input" placeholder="Nombre">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
                                        <input type="text" id="lastName" value="${this.currentUser.lastName}" class="form-input" placeholder="Apellido">
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input type="email" id="email" value="${this.currentUser.email}" class="form-input" placeholder="Email">
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                                    <input type="tel" id="phone" value="${this.currentUser.phone || ''}" class="form-input" placeholder="Teléfono">
                                </div>

                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Biografía</label>
                                    <textarea id="bio" class="form-textarea" placeholder="Cuéntanos sobre ti" rows="3">${this.currentUser.bio || ''}</textarea>
                                </div>

                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save mr-2"></i>Guardar Cambios
                                </button>
                            </form>
                        </div>
                    </div>

                    <!-- Estadísticas -->
                    <div class="card">
                        <div class="card-header">
                            <h2 class="text-xl font-bold text-gray-900">Estadísticas</h2>
                        </div>
                        <div class="card-body">
                            <div class="grid grid-cols-3 gap-4">
                                <div class="text-center">
                                    <div class="text-3xl font-bold text-blue-600">12</div>
                                    <p class="text-sm text-gray-600">Tareas Completadas</p>
                                </div>
                                <div class="text-center">
                                    <div class="text-3xl font-bold text-purple-600">5</div>
                                    <p class="text-sm text-gray-600">Proyectos</p>
                                </div>
                                <div class="text-center">
                                    <div class="text-3xl font-bold text-green-600">8</div>
                                    <p class="text-sm text-gray-600">Equipo</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Información de cuenta -->
                <div>
                    <div class="card">
                        <div class="card-header">
                            <h2 class="text-lg font-bold text-gray-900">Información de Cuenta</h2>
                        </div>
                        <div class="card-body space-y-4">
                            <div>
                                <p class="text-xs text-gray-600 uppercase font-semibold">Usuario</p>
                                <p class="text-gray-900 font-medium">@${this.currentUser.username}</p>
                            </div>
                            <div class="border-t border-gray-200 pt-4">
                                <p class="text-xs text-gray-600 uppercase font-semibold">Rol</p>
                                <p class="text-gray-900 font-medium capitalize">${this.currentUser.role}</p>
                            </div>
                            <div class="border-t border-gray-200 pt-4">
                                <p class="text-xs text-gray-600 uppercase font-semibold">Miembro desde</p>
                                <p class="text-gray-900 font-medium">${this.formatDate(this.currentUser.joinDate)}</p>
                            </div>
                            <div class="border-t border-gray-200 pt-4">
                                <p class="text-xs text-gray-600 uppercase font-semibold">Estado</p>
                                <p class="text-gray-900 font-medium">
                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                                        <span class="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                                        Activo
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Acciones rápidas -->
                    <div class="card mt-6">
                        <div class="card-body space-y-2">
                            <button id="downloadDataBtn" class="w-full btn btn-secondary text-sm justify-center">
                                <i class="fas fa-download mr-2"></i>Descargar Datos
                            </button>
                            <button id="changePasswordBtn" class="w-full btn btn-secondary text-sm justify-center">
                                <i class="fas fa-key mr-2"></i>Cambiar Contraseña
                            </button>
                            <button id="logoutBtn" class="w-full btn text-sm justify-center" style="color: #dc2626; border-color: #fecaca; background-color: #fee2e2; font-weight: 500;">
                                <i class="fas fa-sign-out-alt mr-2"></i>Cerrar Sesión
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        // Tabs
        const tabs = this.container.querySelectorAll('.profile-tab');
        tabs.forEach(tab => {
            tab.onclick = (e) => {
                e.preventDefault();
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            };
        });

        // Form de perfil
        const profileForm = this.container.querySelector('#profileForm');
        if (profileForm) {
            profileForm.onsubmit = (e) => this.handleProfileSubmit(e);
        }

        // Botones de acción
        const downloadBtn = this.container.querySelector('#downloadDataBtn');
        if (downloadBtn) {
            downloadBtn.onclick = () => this.downloadUserData();
        }

        const changePasswordBtn = this.container.querySelector('#changePasswordBtn');
        if (changePasswordBtn) {
            changePasswordBtn.onclick = () => this.showChangePasswordModal();
        }

        const logoutBtn = this.container.querySelector('#logoutBtn');
        if (logoutBtn) {
            logoutBtn.onclick = () => this.handleLogout();
        }
    }

    /**
     * Cambiar tab
     */
    switchTab(tabName) {
        this.activeTab = tabName;

        // Actualizar tabs activos
        const tabs = this.container.querySelectorAll('.profile-tab');
        tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active', 'border-b-2', 'border-blue-600');
                tab.classList.remove('text-gray-700');
            } else {
                tab.classList.remove('active', 'border-b-2', 'border-blue-600');
                tab.classList.add('text-gray-700');
            }
        });

        // Actualizar contenido
        const contentDiv = this.container.querySelector('#profileContent');
        if (tabName === 'profile') {
            contentDiv.innerHTML = this.getProfileTabContent();
        } else if (tabName === 'settings') {
            contentDiv.innerHTML = this.getSettingsTabContent();
        } else if (tabName === 'security') {
            contentDiv.innerHTML = this.getSecurityTabContent();
        }

        this.setupEventListeners();
    }

    /**
     * Contenido del tab de configuración
     */
    getSettingsTabContent() {
        return `
            <div class="card">
                <div class="card-header">
                    <h2 class="text-xl font-bold text-gray-900">Configuración de Notificaciones</h2>
                </div>
                <div class="card-body space-y-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-medium text-gray-900">Email de tareas asignadas</h3>
                            <p class="text-sm text-gray-600">Recibir notificaciones por email</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" checked>
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>

                    <div class="border-t border-gray-200 pt-4 flex items-center justify-between">
                        <div>
                            <h3 class="font-medium text-gray-900">Recordatorios de proyectos</h3>
                            <p class="text-sm text-gray-600">Notificaciones de hitos próximos</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer" checked>
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>

                    <div class="border-t border-gray-200 pt-4 flex items-center justify-between">
                        <div>
                            <h3 class="font-medium text-gray-900">Actualizaciones del sistema</h3>
                            <p class="text-sm text-gray-600">Noticias sobre nuevas características</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" class="sr-only peer">
                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Contenido del tab de seguridad
     */
    getSecurityTabContent() {
        return `
            <div class="space-y-6">
                <!-- Cambiar contraseña -->
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-xl font-bold text-gray-900">Cambiar Contraseña</h2>
                    </div>
                    <div class="card-body">
                        <form id="changePasswordForm" class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña Actual</label>
                                <input type="password" id="currentPassword" class="form-input" placeholder="Contraseña actual" required>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Nueva Contraseña</label>
                                <input type="password" id="newPassword" class="form-input" placeholder="Nueva contraseña" required>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña</label>
                                <input type="password" id="confirmPassword" class="form-input" placeholder="Confirmar contraseña" required>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-lock mr-2"></i>Actualizar Contraseña
                            </button>
                        </form>
                    </div>
                </div>

                <!-- Sesiones activas -->
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-xl font-bold text-gray-900">Sesiones Activas</h2>
                    </div>
                    <div class="card-body">
                        <div class="space-y-3">
                            <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
                                <div class="flex items-center">
                                    <i class="fas fa-desktop text-blue-600 mr-3"></i>
                                    <div>
                                        <p class="font-medium text-gray-900">Windows PC</p>
                                        <p class="text-sm text-gray-600">Última actividad: Hace 2 minutos</p>
                                    </div>
                                </div>
                                <span class="text-xs font-semibold text-green-600">ACTIVA</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Información de seguridad -->
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-xl font-bold text-gray-900">Verificación de Identidad</h2>
                    </div>
                    <div class="card-body">
                        <div class="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded">
                            <div class="flex items-center">
                                <i class="fas fa-check-circle text-green-600 mr-3"></i>
                                <div>
                                    <p class="font-medium text-gray-900">Email verificado</p>
                                    <p class="text-sm text-gray-600">${this.currentUser.email}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Manejar envío de formulario de perfil
     */
    async handleProfileSubmit(e) {
        e.preventDefault();

        const firstName = document.querySelector('#firstName')?.value || '';
        const lastName = document.querySelector('#lastName')?.value || '';
        const email = document.querySelector('#email')?.value || '';
        const phone = document.querySelector('#phone')?.value || '';
        const bio = document.querySelector('#bio')?.value || '';

        try {
            const updatedUser = {
                ...this.currentUser,
                firstName,
                lastName,
                email,
                phone,
                bio
            };

            await this.authService.updateProfile(updatedUser);
            this.currentUser = updatedUser;
            this.showSuccess('¡Perfil actualizado exitosamente!');

        } catch (error) {
            console.error('Error updating profile:', error);
            this.showError('Error al actualizar el perfil');
        }
    }

    /**
     * Mostrar modal de cambio de contraseña
     */
    showChangePasswordModal() {
        console.log('Change password modal not implemented yet');
    }

    /**
     * Descargar datos del usuario
     */
    downloadUserData() {
        const userData = {
            user: this.currentUser,
            downloadDate: new Date().toISOString()
        };

        const jsonString = JSON.stringify(userData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user-data-${Date.now()}.json`;
        link.click();
        URL.revokeObjectURL(url);

        this.showSuccess('Datos descargados exitosamente');
    }

    /**
     * Manejar logout
     */
    async handleLogout() {
        this.showConfirm(
            '¿Deseas cerrar sesión?',
            async () => {
                try {
                    await this.authService.logout();
                    window.dispatchEvent(new CustomEvent('logout'));

                } catch (error) {
                    console.error('Error logging out:', error);
                    this.showError('Error al cerrar sesión');
                }
            }
        );
    }

    /**
     * Capitalizar texto
     */
    capitalize(text) {
        return text.charAt(0).toUpperCase() + text.slice(1);
    }
}