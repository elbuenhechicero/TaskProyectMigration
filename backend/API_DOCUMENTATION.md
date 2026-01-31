# Task Manager API - Documentación Completa

## 📋 Descripción del Proyecto

Sistema completo de gestión de tareas desarrollado con FastAPI y MongoDB. Incluye autenticación JWT, CRUD completo, sistema de comentarios, notificaciones, historial de auditoría, dashboard con reportes y optimizaciones avanzadas de rendimiento.

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico
- **Backend**: FastAPI 0.128.0 (Python 3.14+)
- **Base de Datos**: MongoDB Atlas
- **Autenticación**: JWT con bcrypt
- **Caché**: Sistema en memoria con TTL
- **Monitoreo**: Middleware personalizado + psutil
- **Documentación**: Swagger UI automática

### Estructura del Proyecto
```
backend/
├── app/
│   ├── core/                 # Configuración central
│   │   ├── config.py        # Settings y variables de entorno
│   │   └── database.py      # Conexión y gestión de MongoDB
│   ├── models/              # Modelos Pydantic
│   │   ├── user.py         # Usuarios y autenticación
│   │   ├── project.py      # Proyectos
│   │   ├── task.py         # Tareas
│   │   ├── comment.py      # Comentarios
│   │   ├── notification.py # Notificaciones
│   │   ├── history.py      # Historial de auditoría
│   │   └── dashboard.py    # Modelos de dashboard
│   ├── routers/            # Endpoints de API
│   │   ├── auth.py         # Autenticación (login, register)
│   │   ├── users.py        # Gestión de usuarios
│   │   ├── projects.py     # CRUD de proyectos
│   │   ├── tasks.py        # CRUD de tareas
│   │   ├── comments.py     # Sistema de comentarios
│   │   ├── notifications.py # Gestión de notificaciones
│   │   ├── history.py      # Historial y auditoría
│   │   ├── dashboard.py    # Reportes y estadísticas
│   │   └── admin.py        # Administración y monitoreo
│   ├── utils/              # Utilidades
│   │   ├── security.py     # JWT y hashing de contraseñas
│   │   ├── dependencies.py # Dependencias de FastAPI
│   │   ├── cache.py        # Sistema de caché
│   │   ├── history.py      # Registro de auditoría
│   │   └── notification_service.py # Servicio de notificaciones
│   ├── middleware/         # Middleware personalizado
│   │   └── logging_middleware.py # Logging y métricas
│   └── config/            # Configuraciones específicas
│       └── production.py  # Settings de producción
├── main.py               # Punto de entrada de la aplicación
├── requirements.txt      # Dependencias
└── scripts/             # Scripts de utilidad
    ├── setup_complete.py    # Instalación completa
    ├── setup_production.py # Configuración producción
    └── populate_test_data.py # Datos de prueba
```

## 🔗 API Endpoints

### Autenticación
- `POST /api/v1/auth/register` - Registro de usuarios
- `POST /api/v1/auth/login` - Inicio de sesión
- `GET /api/v1/auth/me` - Perfil del usuario actual

### Usuarios
- `GET /api/v1/users/` - Listar usuarios
- `GET /api/v1/users/{user_id}` - Obtener usuario específico
- `PUT /api/v1/users/{user_id}` - Actualizar usuario

### Proyectos
- `GET /api/v1/projects/` - Listar proyectos
- `POST /api/v1/projects/` - Crear proyecto
- `GET /api/v1/projects/{project_id}` - Obtener proyecto
- `PUT /api/v1/projects/{project_id}` - Actualizar proyecto
- `DELETE /api/v1/projects/{project_id}` - Eliminar proyecto

### Tareas
- `GET /api/v1/tasks/` - Listar tareas con filtros
- `POST /api/v1/tasks/` - Crear tarea
- `GET /api/v1/tasks/{task_id}` - Obtener tarea
- `PUT /api/v1/tasks/{task_id}` - Actualizar tarea
- `DELETE /api/v1/tasks/{task_id}` - Eliminar tarea

### Comentarios y Colaboración
- `POST /api/v1/comments/` - Crear comentario
- `GET /api/v1/comments/task/{task_id}` - Comentarios de tarea
- `PUT /api/v1/comments/{comment_id}` - Actualizar comentario
- `DELETE /api/v1/comments/{comment_id}` - Eliminar comentario

### Dashboard y Reportes
- `GET /api/v1/dashboard/stats` - Estadísticas generales
- `GET /api/v1/dashboard/charts` - Datos para gráficos
- `GET /api/v1/dashboard/reports` - Reportes detallados

### Notificaciones
- `GET /api/v1/notifications/` - Listar notificaciones
- `PUT /api/v1/notifications/{notification_id}/read` - Marcar como leída

### Historial y Auditoría
- `GET /api/v1/history/user/{user_id}` - Historial de usuario
- `GET /api/v1/history/task/{task_id}` - Historial de tarea
- `GET /api/v1/history/project/{project_id}` - Historial de proyecto

### Administración (Requiere privilegios de admin)
- `GET /api/v1/admin/system/status` - Estado del sistema
- `GET /api/v1/admin/metrics/requests` - Métricas de requests
- `GET /api/v1/admin/metrics/endpoints` - Estadísticas por endpoint
- `GET /api/v1/admin/metrics/realtime` - Métricas en tiempo real

## 🔐 Sistema de Autenticación

### JWT (JSON Web Tokens)
- **Algoritmo**: HS256
- **Expiración**: 60 minutos
- **Formato**: `Bearer {token}`

### Registro de Usuario
```json
POST /api/v1/auth/register
{
    "username": "usuario",
    "email": "usuario@ejemplo.com",
    "full_name": "Usuario Ejemplo",
    "password": "contraseña123"
}
```

### Inicio de Sesión
```json
POST /api/v1/auth/login
{
    "username": "usuario",
    "password": "contraseña123"
}
```

### Respuesta de Login
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

## 📊 Características Avanzadas

### Sistema de Caché
- **Tipo**: En memoria con TTL
- **Duración**: 300 segundos (configurable)
- **Invalidación**: Automática en operaciones CRUD
- **Endpoints cacheados**: Dashboard, reportes, estadísticas

### Middleware de Logging
- **Request tracking**: Tiempo de respuesta, status codes
- **Rate limiting**: 120 requests/minuto por IP
- **Security headers**: CORS, XSS, HSTS automáticos
- **Métricas en tiempo real**: CPU, memoria, requests activos

### Sistema de Notificaciones
- **Automáticas**: Asignación de tareas, comentarios, cambios de estado
- **Tipos**: INFO, WARNING, SUCCESS, ERROR
- **Mentions**: Sistema de @menciones en comentarios
- **Estado**: Leídas/No leídas con timestamps

### Historial de Auditoría
- **Tracking completo**: Todas las operaciones CRUD
- **Metadatos**: Usuario, timestamp, cambios específicos
- **Consultas**: Por usuario, tarea, proyecto o fecha
- **Retención**: Configurable (por defecto 1 año)

## 🚀 Optimizaciones de Rendimiento

### Base de Datos
```javascript
// Índices optimizados en MongoDB
db.users.createIndex({"username": 1}, {unique: true})
db.users.createIndex({"email": 1}, {unique: true})
db.projects.createIndex({"created_by": 1})
db.tasks.createIndex({"project_id": 1, "status": 1})
db.tasks.createIndex({"assigned_to": 1, "due_date": 1})
db.comments.createIndex({"task_id": 1, "created_at": -1})
db.notifications.createIndex({"user_id": 1, "read": 1})
db.history.createIndex({"entity_id": 1, "entity_type": 1})
```

### Consultas Optimizadas
- **Agregación MongoDB**: Para estadísticas del dashboard
- **Paginación**: En listas grandes de datos
- **Filtros eficientes**: Usando índices compuestos
- **Proyección selectiva**: Solo campos necesarios

## 🛡️ Seguridad

### Headers de Seguridad
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
```

### Rate Limiting
- **Global**: 120 requests/minuto por IP
- **Login**: 1 request/segundo (burst: 5)
- **Headers informativos**: X-RateLimit-Limit, X-RateLimit-Remaining

### Validación de Datos
- **Pydantic models**: Validación automática de tipos
- **Sanitización**: Prevención de inyección
- **Longitud de contraseñas**: Manejo seguro de bcrypt (72 bytes)

## 📈 Monitoreo y Métricas

### Métricas del Sistema
```python
# Ejemplo de respuesta de métricas
{
    "active_requests": 3,
    "total_requests_5min": 150,
    "requests_per_minute": 30.0,
    "average_response_time": 0.045,
    "error_rate": 0.02,
    "system": {
        "cpu_percent": 25.3,
        "memory_percent": 68.2,
        "disk_percent": 45.1
    }
}
```

### Endpoints de Monitoreo
- `/api/v1/admin/metrics/realtime` - Métricas en tiempo real
- `/api/v1/admin/metrics/requests` - Historial de requests
- `/api/v1/admin/metrics/endpoints` - Estadísticas por endpoint

## ⚙️ Configuración

### Variables de Entorno
```bash
# Base de datos
MONGODB_URI=mongodb+srv://user:pass@cluster/database
DATABASE_NAME=task_manager

# Seguridad
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]

# Rendimiento
CACHE_TTL=300
RATE_LIMIT_PER_MINUTE=120
```

### Configuración de Producción
Ver `app/config/production.py` para configuraciones específicas de producción incluyendo logging, índices optimizados y configuraciones de seguridad.

## 🧪 Testing

### Swagger UI
Accede a la documentación interactiva en:
- **Desarrollo**: http://localhost:8000/docs
- **Producción**: https://tu-dominio.com/docs

### Ejemplo de Flujo Completo
1. Registrar usuario
2. Iniciar sesión y obtener token
3. Crear proyecto
4. Crear tareas en el proyecto
5. Asignar tareas a usuarios
6. Agregar comentarios
7. Verificar notificaciones
8. Consultar dashboard y reportes

## 🔧 Mantenimiento

### Limpieza Automática
```python
# Ejecutar limpieza de datos antiguos
GET /api/v1/admin/maintenance/cleanup
```

### Cache Management
```python
# Limpiar cache
POST /api/v1/admin/cache/clear

# Estadísticas de cache
GET /api/v1/admin/cache/stats
```

### Logs
Los logs se guardan en el directorio `logs/` con rotación automática:
- `app.log` - Logs de aplicación
- `access.log` - Logs de acceso
- `error.log` - Logs de errores

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [JWT.io](https://jwt.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)