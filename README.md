# Task Manager - Sistema de Gestión de Tareas

![Task Manager](https://img.shields.io/badge/FastAPI-0.128.0-green) ![Python](https://img.shields.io/badge/Python-3.14+-blue) ![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green) ![JWT](https://img.shields.io/badge/JWT-Auth-orange) ![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 📋 Descripción

Sistema completo de gestión de tareas desarrollado con **FastAPI** y **MongoDB**. Migración exitosa desde una aplicación JavaScript legacy a una arquitectura moderna con autenticación JWT, sistema de notificaciones, auditoría completa y optimizaciones avanzadas de rendimiento.

### ✨ Características Principales

- 🔐 **Autenticación JWT** con bcrypt seguro
- 📊 **Dashboard interactivo** con reportes en tiempo real
- 💬 **Sistema de comentarios** con @menciones
- 🔔 **Notificaciones automáticas** inteligentes
- 📝 **Historial de auditoría** completo
- ⚡ **Cache en memoria** con invalidación automática
- 🛡️ **Middleware de seguridad** y rate limiting
- 📈 **Monitoreo en tiempo real** con métricas detalladas
- 🚀 **Listo para producción** en render.com

## 🏗️ Arquitectura

### Stack Tecnológico
```
Frontend: JavaScript Legacy → Modern FastAPI Backend
Backend: FastAPI 0.128.0 (Python 3.14+)
Database: MongoDB Atlas
Auth: JWT + bcrypt
Cache: In-memory with TTL
Monitoring: Custom middleware + psutil
Deployment: Render.com ready
```

### Endpoints Principales
```
🔐 Auth:        /api/v1/auth/*
👥 Users:       /api/v1/users/*
📁 Projects:    /api/v1/projects/*
✅ Tasks:       /api/v1/tasks/*
💬 Comments:    /api/v1/comments/*
🔔 Notifications: /api/v1/notifications/*
📊 Dashboard:   /api/v1/dashboard/*
📝 History:     /api/v1/history/*
⚙️ Admin:       /api/v1/admin/*
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.14+
- MongoDB Atlas account
- Git

### 1. Clonación e Instalación
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/TaskProyectMigration.git
cd TaskProyectMigration/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración
```bash
# Crear archivo .env
cp .env.example .env

# Editar variables de entorno
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/task_manager
SECRET_KEY=tu-clave-super-secreta
```

### 3. Ejecutar
```bash
# Modo desarrollo
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Modo producción
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Verificar
- 🌐 **API**: http://localhost:8000
- 📚 **Swagger UI**: http://localhost:8000/docs
- 🩺 **Health Check**: http://localhost:8000/health

## 📊 Funcionalidades Avanzadas

### Sistema de Cache
```python
# Cache automático con TTL
@cache_response(ttl=300)
async def get_dashboard_stats():
    # Datos cacheados por 5 minutos
    pass
```

### Notificaciones Inteligentes
```python
# Notificaciones automáticas
task_assigned → notification_created
comment_added → mentions_notified
status_changed → stakeholders_notified
```

### Auditoría Completa
```python
# Todo tracked automáticamente
user_created → history_entry
task_updated → audit_log
project_deleted → change_record
```

### Métricas en Tiempo Real
```bash
GET /api/v1/admin/metrics/realtime
{
    "active_requests": 5,
    "requests_per_minute": 45,
    "cpu_percent": 23.5,
    "memory_percent": 67.2
}
```

## 📁 Estructura del Proyecto

```
TaskProyectMigration/
├── 📁 backend/                 # Nueva API FastAPI
│   ├── 📁 app/
│   │   ├── 📁 core/           # Configuración
│   │   ├── 📁 models/         # Modelos Pydantic  
│   │   ├── 📁 routers/        # Endpoints API
│   │   ├── 📁 utils/          # Utilidades
│   │   ├── 📁 middleware/     # Middleware personalizado
│   │   └── 📁 config/         # Configuraciones
│   ├── main.py               # Punto de entrada
│   ├── requirements.txt      # Dependencias
│   └── 📁 scripts/           # Scripts útiles
│
├── 📁 frontend_legacy/        # Frontend JavaScript original
│   ├── app.js               # Lógica principal
│   ├── index.html           # UI principal
│   └── style.css            # Estilos
│
├── 📚 API_DOCUMENTATION.md   # Documentación completa
├── 🚀 DEPLOYMENT_GUIDE.md    # Guía de deploy render.com
└── 📝 README.md             # Este archivo
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Archivo .env
MONGODB_URI=mongodb+srv://user:pass@cluster/database
DATABASE_NAME=task_manager
SECRET_KEY=clave-super-secreta-256-bits
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
CACHE_TTL=300
RATE_LIMIT_PER_MINUTE=120
```

### Índices MongoDB Optimizados
```javascript
// Ejecutar en MongoDB
db.users.createIndex({"username": 1}, {unique: true})
db.tasks.createIndex({"project_id": 1, "status": 1})
db.notifications.createIndex({"user_id": 1, "read": 1})
db.history.createIndex({"entity_id": 1, "timestamp": -1})
```

## 🧪 Testing

### Swagger UI Interactivo
1. Ve a http://localhost:8000/docs
2. Registra un usuario en `POST /api/v1/auth/register`
3. Inicia sesión en `POST /api/v1/auth/login`
4. Copia el token y autorízate con `Bearer {token}`
5. Prueba todos los endpoints disponibles

### Datos de Prueba
```bash
# Poblar con datos de prueba
python scripts/populate_test_data.py
```

### Verificación del Sistema
```bash
# Script de verificación completa
python scripts/setup_complete.py
```

## 📈 Monitoreo y Métricas

### Dashboard de Admin
- **Métricas en tiempo real**: CPU, RAM, requests activos
- **Estadísticas de API**: Endpoints más usados, tiempos de respuesta
- **Health checks**: Estado de base de datos y servicios
- **Cache management**: Estadísticas y limpieza

### Logging Avanzado
```python
# Logs estructurados automáticos
INFO: Request started: GET /api/v1/tasks/ from 127.0.0.1
INFO: Request completed: GET /api/v1/tasks/ -> 200 in 0.045s
```

## 🚀 Deployment en Render.com

### Configuración Rápida
```yaml
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Variables de Entorno en Render
```bash
MONGODB_URI=tu-connection-string
SECRET_KEY=clave-produccion-segura
DEBUG=false
ALLOWED_ORIGINS=["https://tu-frontend.onrender.com"]
```

📖 **Ver guía completa**: [DEPLOYMENT_GUIDE.md](backend/DEPLOYMENT_GUIDE.md)

## 🛡️ Seguridad

### Características de Seguridad
- ✅ **JWT con expiración** (60 min configurable)
- ✅ **bcrypt** para hashing de contraseñas
- ✅ **Rate limiting** (120 req/min por IP)
- ✅ **CORS** configurado correctamente
- ✅ **Headers de seguridad** automáticos
- ✅ **Validación de entrada** con Pydantic
- ✅ **SQL Injection** protection (NoSQL)

### Headers de Seguridad Automáticos
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

## 📊 Rendimiento

### Optimizaciones Implementadas
- ⚡ **Cache en memoria** con TTL automático
- 🔄 **Invalidación inteligente** de cache
- 📊 **Índices MongoDB** optimizados
- 🚀 **Consultas agregadas** eficientes
- 💾 **Connection pooling** automático
- 📈 **Métricas de rendimiento** en tiempo real

### Benchmarks
```
Endpoints simples: ~5ms promedio
Dashboard stats: ~45ms (con cache)
Búsquedas complejas: ~120ms
Operaciones CRUD: ~15ms promedio
```

## 🏆 Progreso del Proyecto

### ✅ Commits Completados (15/15)
1. ✅ **Setup inicial** - Configuración base FastAPI
2. ✅ **Estructura MVC** - Organización de código
3. ✅ **Autenticación JWT** - Sistema de login completo
4. ✅ **CRUD Usuarios** - Gestión de usuarios
5. ✅ **CRUD Proyectos** - Gestión de proyectos  
6. ✅ **CRUD Tareas** - Funcionalidad core
7. ✅ **Sistema de Estados** - Workflow de tareas
8. ✅ **Filtros y Búsqueda** - Consultas avanzadas
9. ✅ **Sistema de Comentarios** - Colaboración
10. ✅ **Historial de Auditoría** - Tracking completo
11. ✅ **Notificaciones** - Sistema automático
12. ✅ **Dashboard y Reportes** - Análisis de datos
13. ✅ **Sistema completo integrado** - Testing E2E
14. ✅ **Optimizaciones y caché** - Rendimiento
15. ✅ **Documentación y deployment** - Producción ready

### 🎯 Objetivos Alcanzados
- ✅ **15 commits** completados exitosamente
- ✅ **Migración completa** desde JavaScript legacy
- ✅ **API moderna** con FastAPI
- ✅ **Sistema productivo** listo para render.com
- ✅ **Documentación completa** incluida
- ✅ **Optimizaciones avanzadas** implementadas

## 🤝 Contribución

### Cómo Contribuir
1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Desarrollo Local
```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest

# Linting
flake8 app/

# Formateo
black app/
```

## 📝 Changelog

### v1.0.0 (2026-01-31)
- 🎉 **Migración completa** desde JavaScript legacy
- ✅ **15 commits implementados** exitosamente
- 🚀 **Sistema de producción** listo
- 📚 **Documentación completa** incluida
- ⚡ **Optimizaciones avanzadas** de rendimiento
- 🛡️ **Seguridad robusta** implementada

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: Migración JavaScript → FastAPI
- **Arquitectura**: FastAPI + MongoDB + JWT
- **Deployment**: Render.com optimizado

## 🔗 Enlaces Útiles

- 📚 [Documentación de API](backend/API_DOCUMENTATION.md)
- 🚀 [Guía de Deployment](backend/DEPLOYMENT_GUIDE.md)
- 🌐 [Swagger UI](http://localhost:8000/docs)
- 🩺 [Health Check](http://localhost:8000/health)
- 📊 [Admin Dashboard](http://localhost:8000/api/v1/admin/system/status)

## ⭐ Reconocimientos

- FastAPI por el framework increíble
- MongoDB Atlas por la base de datos confiable
- Render.com por el hosting simplificado
- Comunidad de Python por las herramientas excelentes

---

**¡Migración exitosa completada! 🎉**

*De JavaScript legacy a FastAPI moderno en 15 commits* ⚡

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

- Todos los datos se guardan en localStorage del navegador
- Los datos persisten entre sesiones
- Para limpiar los datos, usa la consola del navegador: `localStorage.clear()`
- Compatible con cualquier navegador moderno (Chrome, Firefox, Safari, Edge)
