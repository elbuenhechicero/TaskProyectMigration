# Task Manager - Arquitectura MVC Completa

## 📋 Descripción General

Sistema de gestión de tareas profesional construido con arquitectura MVC pura (Model-View-Controller), separación clara de responsabilidades, e integración con API FastAPI backend.

**Tecnologías Frontend:**
- Vanilla JavaScript (ES6+) con patrón MVC
- Tailwind CSS 3.x para estilos responsive
- Alpine.js 3.x para interactividad
- Font Awesome 6.4.0 para iconografía

**Tecnologías Backend:**
- FastAPI 0.60.1
- Uvicorn 0.40.0
- Motor 2.5.1 (async MongoDB driver)
- Pydantic 1.10.26 para validación

## 🏗️ Estructura de Carpetas

```
TaskProyectMigration/
├── frontend/                          # Aplicación web MVC
│   ├── index.html                    # HTML principal
│   ├── css/
│   │   └── main.css                  # Tailwind + estilos personalizados
│   └── js/
│       ├── models/                   # Capas de Modelos
│       │   ├── BaseModel.js          # Clase base para todas las modelos
│       │   ├── User.js               # Modelo de usuario
│       │   ├── Task.js               # Modelo de tarea
│       │   └── Project.js            # Modelo de proyecto
│       ├── services/                 # Capas de Servicios (Business Logic)
│       │   ├── ApiService.js         # Cliente HTTP base con auth
│       │   ├── AuthService.js        # Autenticación y sesión
│       │   ├── TaskService.js        # Operaciones CRUD de tareas
│       │   └── ProjectService.js     # Operaciones CRUD de proyectos
│       ├── views/                    # Capas de Vistas (Presentación)
│       │   ├── BaseView.js           # Clase base para todas las vistas
│       │   ├── LoginView.js          # Vista de autenticación
│       │   ├── DashboardView.js      # Vista de panel principal
│       │   ├── TaskView.js           # Vista de gestión de tareas
│       │   ├── ProjectView.js        # Vista de gestión de proyectos
│       │   └── ProfileView.js        # Vista de perfil de usuario
│       ├── controllers/              # Capas de Controladores
│       │   ├── AppController.js      # Controlador principal (router)
│       │   ├── TaskController.js     # Lógica de negocio de tareas
│       │   └── ProjectController.js  # Lógica de negocio de proyectos
│       └── utils/                    # Utilidades compartidas
│           ├── ValidationHelper.js   # Validación de formularios
│           ├── DateHelper.js         # Manejo de fechas
│           └── Toast.js              # Sistema de notificaciones
├── backend/                          # API FastAPI
│   ├── main.py                       # Punto de entrada de la aplicación
│   ├── requirements.txt              # Dependencias Python
│   ├── Procfile                      # Configuración para Render.com
│   ├── runtime.txt                   # Versión de Python
│   └── render.yaml                   # Configuración de despliegue
├── app.js                            # (Archivo antiguo - descontinuado)
├── index.html                        # (Archivo antiguo - descontinuado)
├── style.css                         # (Archivo antiguo - descontinuado)
└── README.md                         # Documentación del proyecto
```

## 🎯 Patrones de Arquitectura

### 1. Model-View-Controller (MVC)

```
┌─────────────────────────────────────────┐
│  User Interaction (View)                │
│  ├─ TaskView.js                         │
│  ├─ ProjectView.js                      │
│  └─ ProfileView.js                      │
└──────────┬────────────────────────────┬─┘
           │                            │
    ┌──────▼────────┐         ┌────────▼─────┐
    │ Controller    │         │ Services     │
    │ AppController │────────▶│ TaskService  │
    │ TaskControl.  │         │ ProjectServ. │
    │ ProjectControl│         │ AuthService  │
    └───────────────┘         └────────┬─────┘
           │                          │
    ┌──────▼──────────────────────────▼──────┐
    │  Models (Domain Logic)                  │
    │  ├─ Task.js                             │
    │  ├─ Project.js                          │
    │  ├─ User.js                             │
    │  └─ BaseModel.js (abstract)             │
    └─────────────────────────────────────────┘
            │
    ┌───────▼──────────────┐
    │  API Service         │
    │  ├─ HTTP Requests    │
    │  ├─ Auth Tokens      │
    │  └─ Error Handling   │
    └──────────┬───────────┘
               │
    ┌──────────▼────────────┐
    │  FastAPI Backend      │
    │  (localhost:8000)     │
    └───────────────────────┘
```

### 2. Separación de Responsabilidades

**Models (Modelos):**
- Representan el dominio del negocio
- Contienen lógica de negocio específica
- Validan sus propios datos
- No tienen acceso a servicios o vistas

**Services (Servicios):**
- Manejan la comunicación con APIs
- Implementan lógica de aplicación
- Proporcionan datos modificados a los controladores
- Gestionan estados globales de autenticación

**Views (Vistas):**
- Responsables solo de la presentación
- Renderizan elementos DOM
- Manejan eventos del usuario
- Comunican cambios a través de controladores

**Controllers (Controladores):**
- Orquestan la interacción entre vistas y servicios
- Manejan eventos globales
- Gestionan el flujo de navegación
- Implementan la lógica de negocio de nivel de aplicación

### 3. Flujo de Datos

```
User Input (Click, Form Submit)
    ↓
View Event Listener
    ↓
Controller Handler
    ↓
Service Method (API Call)
    ↓
Model Validation
    ↓
API Response / Database
    ↓
Model Update
    ↓
View Re-render
    ↓
User Sees Update
```

## 📦 Componentes Principales

### Modelos (Models)

#### BaseModel.js
```javascript
class BaseModel {
    validate()              // Validar datos del modelo
    toJSON()               // Serializar a JSON
    update(data)           // Actualizar propiedades
    clone()                // Crear una copia
    getValidationRules()   // Obtener reglas de validación
}
```

#### Task.js
```javascript
class Task extends BaseModel {
    static VALID_STATUSES = ['Pendiente', 'En Progreso', 'Completada', 'Bloqueada', 'Cancelada']
    static VALID_PRIORITIES = ['Baja', 'Media', 'Alta', 'Crítica']
    
    isOverdue()            // ¿Está vencida?
    getProgress()          // Obtener progreso
    getDaysUntilDue()      // Días hasta la fecha límite
    markAsCompleted()      // Marcar como completada
    getPriorityClass()     // Clase CSS para prioridad
}
```

#### Project.js
```javascript
class Project extends BaseModel {
    addTeamMember(email)        // Agregar miembro al equipo
    removeTeamMember(email)     // Remover miembro
    isTeamMember(email)         // ¿Es miembro del equipo?
    getStatusInfo()             // Info de estado con colores
    markAsCompleted()           // Marcar como completado
    getDuration()               // Duración del proyecto
    isOverdue()                 // ¿Está vencido?
}
```

#### User.js
```javascript
class User extends BaseModel {
    isValidEmail()         // Validar email
    getFullName()          // Obtener nombre completo
    isAdmin()              // ¿Es administrador?
    toSafeJSON()           // JSON sin contraseña
}
```

### Servicios (Services)

#### ApiService.js (Base)
```javascript
class ApiService {
    setAuthToken(token)         // Establecer token de auth
    getHeaders()                // Headers con Bearer token
    request(method, endpoint, data)  // Hacer request HTTP
    validateToken()             // Validar token actual
}

class ApiError extends Error {
    isAuthError()              // ¿Error de autenticación?
    isValidationError()        // ¿Error de validación?
    isServerError()            // ¿Error del servidor?
}
```

#### AuthService.js
```javascript
class AuthService extends ApiService {
    login(username, password)        // Iniciar sesión
    register(userData)               // Registrarse
    logout()                         // Cerrar sesión
    loadCurrentUser()                // Cargar usuario actual
    saveCurrentUser(user)            // Guardar usuario
    refreshToken()                   // Refrescar token
    isAuthenticated()                // ¿Autenticado?
    changePassword(oldPwd, newPwd)   // Cambiar contraseña
    updateProfile(user)              // Actualizar perfil
}
```

#### TaskService.js
```javascript
class TaskService extends ApiService {
    getAllTasks()                    // Obtener todas las tareas
    getTaskById(id)                  // Obtener tarea por ID
    createTask(task)                 // Crear nueva tarea
    updateTask(id, data)             // Actualizar tarea
    deleteTask(id)                   // Eliminar tarea
    getTasksByProject(projectId)     // Tareas por proyecto
    getTasksByUser(userId)           // Tareas por usuario
    getTasksByStatus(status)         // Tareas por estado
    searchTasks(query)               // Buscar tareas
    getTaskStats()                   // Estadísticas
    completeTask(id)                 // Completar tarea
}
```

#### ProjectService.js
```javascript
class ProjectService extends ApiService {
    getAllProjects()                 // Obtener todos los proyectos
    getProjectById(id)               // Obtener proyecto por ID
    createProject(project)           // Crear nuevo proyecto
    updateProject(id, data)          // Actualizar proyecto
    deleteProject(id)                // Eliminar proyecto
    getProjectsByUser(userId)        // Proyectos del usuario
    addTeamMember(projectId, email)  // Agregar miembro
    removeTeamMember(projectId, email) // Remover miembro
    getProjectStats()                // Estadísticas de proyectos
}
```

### Vistas (Views)

#### BaseView.js (Clase Base)
```javascript
class BaseView {
    constructor(containerId)         // Inicializar con contenedor
    render()                         // Renderizar vista (abstract)
    show()                           // Mostrar vista
    hide()                           // Ocultar vista
    createElement(html)              // Crear elemento DOM
    addEventListener(el, event, handler)  // Agregar event listener
    cleanup()                        // Limpiar recursos
    
    // Utilidades de UI
    showError(message)               // Mostrar error
    showSuccess(message)             // Mostrar éxito
    showLoading()                    // Mostrar carga
    hideLoading()                    // Ocultar carga
    showConfirm(message, callback)   // Modal de confirmación
    
    // Utilidades de formato
    formatDate(date)                 // Formatear fecha
    formatRelativeDate(date)         // Formato relativo (hace X)
    escapeHtml(text)                 // Escapar HTML
    truncateText(text, length)       // Truncar texto
}
```

#### LoginView.js
```javascript
class LoginView extends BaseView {
    render()                         // Renderizar tabs de login/registro
    handleLogin(credentials)         // Manejar login
    handleRegister(userData)         // Manejar registro
    switchTab(tabName)               // Cambiar entre tabs
    
    // Características:
    // - Tabs de login y registro
    // - Credenciales de demostración
    // - Toggle de visibilidad de contraseña
    // - Validación en cliente
}
```

#### DashboardView.js
```javascript
class DashboardView extends BaseView {
    render()                         // Renderizar dashboard
    loadDashboardData()              // Cargar datos asincronamente
    calculateStats()                 // Calcular estadísticas
    
    // Secciones:
    // - 4 tarjetas de estadísticas
    // - Lista de tareas recientes
    // - Gráfico de proyectos
    // - Sección de tareas urgentes
    // - Botones de acciones rápidas
}
```

#### TaskView.js
```javascript
class TaskView extends BaseView {
    render()                         // Renderizar vista de tareas
    loadTasksData()                  // Cargar datos
    applyFilters()                   // Aplicar filtros
    
    // Características:
    // - Lista de tareas filtrable
    // - Filtros por estado, prioridad, proyecto
    // - Búsqueda por título/descripción
    // - Checkbox para completar
    // - Botones editar/eliminar
    // - Crear nueva tarea
}
```

#### ProjectView.js
```javascript
class ProjectView extends BaseView {
    render()                         // Renderizar vista de proyectos
    loadProjectsData()               // Cargar datos
    
    // Características:
    // - Grid de proyectos con tarjetas
    // - Barra de progreso por proyecto
    // - Miembros del equipo
    // - Estadísticas generales
    // - Crear nuevo proyecto
}
```

#### ProfileView.js
```javascript
class ProfileView extends BaseView {
    render()                         // Renderizar perfil
    loadUserData()                   // Cargar datos del usuario
    switchTab(tabName)               // Cambiar entre tabs
    
    // Tabs:
    // - Perfil: Editar información
    // - Configuración: Notificaciones
    // - Seguridad: Contraseña, sesiones
}
```

### Controladores (Controllers)

#### AppController.js
```javascript
class AppController {
    constructor()                    // Inicializar app
    init()                           // Setup inicial
    
    // Navegación
    navigate(viewName, data)         // Navegar a vista
    showLogin()                      // Mostrar login
    showDashboard()                  // Mostrar dashboard
    showTasks(filters)               // Mostrar tareas
    showProjects(filters)            // Mostrar proyectos
    showProfile()                    // Mostrar perfil
    
    // Autenticación
    handleLogin(credentials)         // Procesar login
    handleRegister(userData)         // Procesar registro
    handleLogout()                   // Procesar logout
    
    // Utilidades
    handleKeyboardShortcuts(event)   // Atajos de teclado
    handlePopState(event)            // Navegación del browser
    handleGlobalError(error)         // Manejar errores
}
```

**Atajos de Teclado:**
- `Alt + D` → Dashboard
- `Alt + T` → Tareas
- `Alt + P` → Proyectos
- `Ctrl/Cmd + K` → Búsqueda rápida
- `Escape` → Cerrar modales

#### TaskController.js
```javascript
class TaskController {
    constructor(taskService, projectService, taskView)
    
    // Operaciones CRUD
    createTask(taskData)             // Crear tarea
    updateTask(taskId, data)         // Actualizar tarea
    completeTask(taskId)             // Completar tarea
    deleteTask(taskId)               // Eliminar tarea
    
    // Consultas
    getTaskStats()                   // Estadísticas
    getTasksByProject(projectId)     // Tareas por proyecto
    getOverdueTasks()                // Tareas vencidas
    getUrgentTasks()                 // Tareas críticas
    
    // Modificaciones
    assignTask(taskId, userId)       // Asignar usuario
    changePriority(taskId, priority) // Cambiar prioridad
    changeStatus(taskId, status)     // Cambiar estado
}
```

#### ProjectController.js
```javascript
class ProjectController {
    constructor(projectService, taskService, projectView)
    
    // Operaciones CRUD
    createProject(projectData)       // Crear proyecto
    updateProject(projectId, data)   // Actualizar proyecto
    completeProject(projectId)       // Completar proyecto
    deleteProject(projectId)         // Eliminar proyecto
    
    // Consultas
    getProjectStats()                // Estadísticas
    getActiveProjects()              // Proyectos activos
    getCompletedProjects()           // Proyectos completados
    getProjectProgress(projectId)    // Progreso del proyecto
    getOverdueProjects()             // Proyectos vencidos
    
    // Equipo
    addTeamMember(projectId, email)  // Agregar miembro
    removeTeamMember(projectId, email) // Remover miembro
    
    // Tareas
    getProjectTasks(projectId)       // Tareas del proyecto
    changeEndDate(projectId, date)   // Cambiar fecha fin
}
```

### Utilidades (Utils)

#### ValidationHelper.js (520 líneas)
```javascript
// Validaciones de datos
isValidEmail(email)                  // Email válido
isValidPassword(password)            // Contraseña válida
isValidUsername(username)            // Usuario válido
isValidDate(date)                    // Fecha válida
isFutureDate(date)                   // Es fecha futura
isValidDateRange(start, end)         // Rango válido
isPositiveNumber(num)                // Número positivo
isInRange(num, min, max)             // Dentro de rango
isValidLength(text, min, max)        // Longitud válida
isNotEmpty(text)                     // No está vacío
isValidURL(url)                      // URL válida
isValidPhone(phone)                  // Teléfono válido
validateFile(file, rules)            // Validar archivo
validateForm(formElement)            // Validar formulario completo

// Utilidades UI
displayErrors(fieldId, errors)       // Mostrar errores
clearErrors(fieldId)                 // Limpiar errores
setupRealTimeValidation(form)        // Validación al perder foco
```

#### DateHelper.js (540 líneas)
```javascript
// Formateo
formatDate(date, format)             // Formatear fecha
formatRelativeDate(date)             // Hace X tiempo
formatDuration(ms)                   // Duración legible
toInputDate(date)                    // Formato para input
toInputDateTime(date)                // Formato fecha-hora

// Consultas
isOverdue(date)                      // ¿Vencida?
isToday(date)                        // ¿Hoy?
isThisWeek(date)                     // ¿Esta semana?
daysBetween(date1, date2)            // Días entre fechas

// Manipulación
addDays(date, days)                  // Sumar días
startOfDay(date)                     // Inicio del día
endOfDay(date)                       // Fin del día
startOfWeek(date)                    // Inicio de semana
endOfWeek(date)                      // Fin de semana

// Rango de fechas
getDateRange(period)                 // Rango (hoy, semana, mes)

// Utilidades
getDayName(date)                     // Nombre del día
getMonthName(date)                   // Nombre del mes
parseDate(dateString)                // Parsear fecha
toTimestamp(date)                    // A timestamp Unix
fromTimestamp(timestamp)             // De timestamp Unix
isLeapYear(year)                     // ¿Año bisiesto?
getDaysInMonth(month, year)          // Días en mes
```

#### Toast.js (250 líneas)
```javascript
// Sistema de notificaciones global
window.notifications.success(msg)    // Notificación éxito
window.notifications.error(msg)      // Notificación error
window.notifications.warning(msg)    // Notificación advertencia
window.notifications.info(msg)       // Notificación información

// Métodos internos
show(type, message, duration)        // Mostrar toast
createNotification(type, message)    // Crear elemento
remove(id)                           // Remover toast
clearAll()                           // Limpiar todos

// Características:
// - Auto-close configurable
// - Pausa al pasar ratón
// - Botón cerrar
// - Estilos por tipo
```

## 🔄 Flujos Principales

### Flujo de Autenticación
```
1. Usuario ingresa credenciales
2. LoginView captura el formulario
3. AppController.handleLogin() es llamado
4. AuthService.login() hace POST a /login
5. Si éxito: token guardado en localStorage
6. AppController.showDashboard()
7. DashboardView renderiza con datos del usuario
```

### Flujo de Crear Tarea
```
1. Usuario click en "Nueva Tarea"
2. Modal de creación abierto
3. Usuario completa formulario
4. TaskController.createTask() validada
5. TaskService.createTask() hace POST a /tasks
6. API devuelve nueva tarea con ID
7. TaskView re-renderiza la lista
8. Toast muestra éxito
```

### Flujo de Filtrar Tareas
```
1. Usuario selecciona filtro
2. TaskView.applyFilters() lee valores
3. Filtra array de tareas en memoria
4. Re-renderiza solo tareas coincidentes
5. Sin hacer llamadas a API (hasta recargar)
```

## 🔌 Integración API

**Base URL:** `http://localhost:8000` (desarrollo)
**Autenticación:** Bearer token en header

### Endpoints esperados:

```
POST   /login              # Login
POST   /register           # Registro
GET    /tasks              # Obtener tareas
POST   /tasks              # Crear tarea
PUT    /tasks/{id}         # Actualizar tarea
DELETE /tasks/{id}         # Eliminar tarea
GET    /projects           # Obtener proyectos
POST   /projects           # Crear proyecto
PUT    /projects/{id}      # Actualizar proyecto
DELETE /projects/{id}      # Eliminar proyecto
GET    /user               # Obtener usuario actual
PUT    /user               # Actualizar perfil
```

## 🎨 Estilos y Temas

### Tailwind CSS
- Responsive design (mobile-first)
- Componentes personalizados en `main.css`
- Tema de colores: azul primario (#3b82f6)
- Soporta dark mode

### Componentes CSS reutilizables:
```css
.card           /* Tarjeta base */
.btn            /* Botón base */
.btn-primary    /* Botón primario */
.btn-secondary  /* Botón secundario */
.form-input     /* Input de formulario */
.form-select    /* Select de formulario */
.form-textarea  /* Textarea de formulario */
.badge          /* Badge/etiqueta */
.alert          /* Alerta */
```

## 🚀 Características Implementadas

✅ Autenticación completa (login/registro)
✅ Dashboard con estadísticas
✅ Gestión de tareas (CRUD)
✅ Gestión de proyectos (CRUD)
✅ Perfil de usuario
✅ Notificaciones toast
✅ Validación de formularios
✅ Filtrados y búsqueda
✅ Manejo de fechas
✅ Atajos de teclado
✅ Navegación con historial del browser
✅ Fallback a datos mock sin API
✅ Sistema de errores global

## 📝 TODOs para Completar

🔲 Modales de creación/edición (TaskView, ProjectView)
🔲 Detalles de tareas/proyectos
🔲 Gráficos con Chart.js
🔲 Carga de avatares
🔲 Búsqueda global avanzada
🔲 Exportar datos a PDF/Excel
🔲 Integración con calendario
🔲 Comentarios en tareas
🔲 Asignación de tareas
🔲 Recordatorios por email
🔲 Tests unitarios y E2E
🔲 PWA (Service Worker)

## 🌐 Despliegue en Render.com

### Configuración Backend:
```
Build Command:  pip install -r requirements.txt
Start Command:  uvicorn main:app --host 0.0.0.0 --port $PORT
Root Directory: backend/
```

### Pasos:
1. Push a GitHub
2. Crear servicio web en Render.com
3. Conectar repositorio
4. Configurar variables de entorno
5. Desplegar

### Después del despliegue:
Cambiar en `ApiService.js`:
```javascript
baseURL = 'https://tu-api.onrender.com'
```

## 📚 Referencia Rápida de Comandos

```bash
# Desarrollo
# Servir frontend (necesitas simple HTTP server)
python -m http.server 8080

# Backend
cd backend
source fastapi_env/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Git
git add .
git commit -m "mensaje"
git push origin TaskManagerSystem
```

## 🤝 Convenciones de Código

### Nombres
- Clases: `PascalCase` (TaskView, ApiService)
- Métodos/variables: `camelCase` (createTask, getUserData)
- Constantes: `UPPER_SNAKE_CASE` (VALID_STATUSES)
- Archivos: `PascalCase.js` (TaskView.js)

### Estructura
- Comentarios JSDoc para métodos públicos
- Métodos privados con `_` prefijo (convención)
- Async/await preferido sobre .then()
- Error handling con try/catch

### Organización
- Métodos ordenados: constructor, init, handlers, utilidades
- Properties al inicio de la clase
- Métodos públicos antes de privados

## 📞 Soporte

Para preguntas sobre la arquitectura:
1. Revisar comentarios en el código
2. Consultar ARCHITECTURE.md (este archivo)
3. Ver ejemplos en vistas/servicios existentes
4. Revisar flujos en la sección de "Flujos Principales"
