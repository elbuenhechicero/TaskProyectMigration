# Task Manager API - Guía de Deployment en Render.com

## 🚀 Deployment en Render.com

Esta guía te ayudará a deployar la Task Manager API en Render.com, incluyendo la configuración de MongoDB Atlas y todas las variables de entorno necesarias.

## 📋 Prerrequisitos

1. Cuenta en [Render.com](https://render.com)
2. Repositorio Git con el código (GitHub, GitLab, etc.)
3. Cuenta en [MongoDB Atlas](https://cloud.mongodb.com)

## 🗄️ Configuración de MongoDB Atlas

### 1. Crear Cluster de MongoDB
```bash
# Ya tienes configurado:
mongodb+srv://eliose121:rey12116@hechicluster.ee92rpm.mongodb.net/task_manager
```

### 2. Configurar Acceso de Red
- Ve a "Network Access" en MongoDB Atlas
- Agregar IP: `0.0.0.0/0` (para permitir acceso desde Render)
- O usar las IPs específicas de Render si las proporcionan

### 3. Crear Índices de Producción
Ejecuta este script en MongoDB Compass o shell:
```javascript
// Índices para optimizar rendimiento
use task_manager;

// Usuarios
db.users.createIndex({"username": 1}, {unique: true, background: true});
db.users.createIndex({"email": 1}, {unique: true, background: true});

// Proyectos
db.projects.createIndex({"created_by": 1}, {background: true});
db.projects.createIndex({"created_at": -1}, {background: true});

// Tareas
db.tasks.createIndex({"project_id": 1, "status": 1}, {background: true});
db.tasks.createIndex({"assigned_to": 1, "due_date": 1}, {background: true});
db.tasks.createIndex({"created_by": 1}, {background: true});

// Comentarios
db.comments.createIndex({"task_id": 1, "created_at": -1}, {background: true});
db.comments.createIndex({"created_by": 1}, {background: true});

// Notificaciones
db.notifications.createIndex({"user_id": 1, "read": 1}, {background: true});
db.notifications.createIndex({"created_at": -1}, {background: true});

// Historial
db.history.createIndex({"entity_id": 1, "entity_type": 1}, {background: true});
db.history.createIndex({"timestamp": -1}, {background: true});
```

## 🔧 Configuración en Render.com

### 1. Crear Web Service

1. **Conectar repositorio:**
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Clic en "New +" → "Web Service"
   - Conecta tu repositorio Git
   - Selecciona el repositorio del Task Manager

2. **Configuración básica:**
   ```yaml
   Name: task-manager-api
   Region: Oregon (US West) o el más cercano
   Branch: main (o tu rama principal)
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### 2. Variables de Entorno

Agregar en "Environment Variables":

```bash
# Base de datos
MONGODB_URI=mongodb+srv://eliose121:rey12116@hechicluster.ee92rpm.mongodb.net/task_manager
DATABASE_NAME=task_manager

# Seguridad (GENERAR CLAVES NUEVAS PARA PRODUCCIÓN)
SECRET_KEY=CAMBIAR_POR_CLAVE_SUPER_SECRETA_DE_PRODUCCION_256_BITS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Configuration
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS Origins (agregar tu dominio de frontend)
ALLOWED_ORIGINS=["https://tu-frontend.render.com","https://taskmanager-frontend.com"]

# Performance
CACHE_TTL=300
RATE_LIMIT_PER_MINUTE=120

# Logging
LOG_LEVEL=INFO
```

### 3. Generar SECRET_KEY Segura

```python
# Ejecutar en Python para generar clave segura
import secrets
print(secrets.token_urlsafe(32))
# Ejemplo: 'xvz9Q8rK7mN3pL6sT2uW5yA8cF1dG4hJ9mR7sV0xY3zA6bE2nQ5tL8pK'
```

## 📝 Archivo requirements.txt para Producción

Crear en `/backend/requirements.txt`:
```txt
# FastAPI Core
fastapi==0.128.0
uvicorn[standard]==0.24.0

# Database
motor==3.7.1
pymongo==4.16.0

# Authentication
python-jose==3.5.0
bcrypt==5.0.0

# Validation
pydantic==2.12.5
pydantic-settings==2.12.0
email-validator==2.3.0

# Environment
python-dotenv==1.2.1

# System monitoring
psutil==7.2.2

# ASGI server for production
gunicorn==21.2.0
```

## 🐳 Dockerfile para Deployment (Opcional)

Si prefieres usar Docker en Render:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ⚙️ Configuración de Build

En Render, configurar:

### Build Command:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

## 🔍 Health Checks

Render verificará automáticamente:
- **Health Check URL**: `/health`
- **Expected Status**: 200
- **Timeout**: 30s

El endpoint ya está configurado en `main.py`:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "API is running",
        "database": "connected" if mongodb.client else "disconnected"
    }
```

## 🌐 Dominios y HTTPS

### 1. Dominio Gratuito de Render
Tu servicio estará disponible en:
```
https://task-manager-api.onrender.com
```

### 2. Dominio Personalizado (Plan Paid)
Para usar tu propio dominio:
1. Ve a "Settings" → "Custom Domains"
2. Agrega tu dominio
3. Configura los DNS records según las instrucciones

## 📊 Monitoreo en Producción

### Logs en Tiempo Real
```bash
# Ver logs en Render Dashboard
# O usar Render CLI:
render logs task-manager-api
```

### Métricas Disponibles
- CPU Usage
- Memory Usage
- Request Volume
- Error Rates

### Endpoints de Monitoreo
```bash
# Health check
GET https://tu-api.onrender.com/health

# Métricas de sistema (requiere admin)
GET https://tu-api.onrender.com/api/v1/admin/system/status

# Métricas en tiempo real (requiere admin)
GET https://tu-api.onrender.com/api/v1/admin/metrics/realtime
```

## 🔐 Seguridad en Producción

### 1. Variables de Entorno Seguras
- Nunca commitear claves en el código
- Usar variables de entorno de Render
- Generar SECRET_KEY única para producción

### 2. CORS Configuration
```python
# Configurar origins específicos
ALLOWED_ORIGINS=[
    "https://tu-frontend.onrender.com",
    "https://tu-dominio.com"
]
```

### 3. Rate Limiting
El middleware ya incluye rate limiting:
- 120 requests/min por IP
- Headers informativos incluidos

## 🚀 Proceso de Deployment

### 1. Deploy Automático
```bash
# Render hace deployment automático cuando:
git push origin main
```

### 2. Deploy Manual
En Render Dashboard:
1. Ve a tu servicio
2. Clic "Deploy Latest Commit"
3. Monitorear logs durante el deploy

### 3. Rollback (si es necesario)
1. Ve a "Deploys" en Dashboard
2. Selecciona deploy anterior
3. Clic "Rollback to this Deploy"

## 🧪 Testing en Producción

### 1. Verificar Endpoints
```bash
# Health check
curl https://tu-api.onrender.com/health

# API Documentation
https://tu-api.onrender.com/docs

# Register test user
curl -X POST https://tu-api.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "test123"}'
```

### 2. Load Testing (opcional)
```bash
# Usar herramientas como:
# - Apache Bench (ab)
# - wrk
# - Postman Load Testing

# Ejemplo con curl:
for i in {1..10}; do
  curl https://tu-api.onrender.com/health &
done
```

## 📈 Optimizaciones Post-Deploy

### 1. CDN (opcional)
Para assets estáticos, considerar Cloudflare o similar

### 2. Database Connection Pooling
Ya configurado en `motor` con pool size automático

### 3. Caching
Sistema de caché en memoria ya implementado:
- TTL configurable
- Invalidación automática
- Métricas incluidas

## 🔧 Troubleshooting

### Problemas Comunes:

1. **Error de conexión a MongoDB:**
   ```
   Verificar IP whitelist en Atlas
   Verificar connection string
   ```

2. **Error 503 Service Unavailable:**
   ```
   Verificar Build Logs
   Verificar Start Command
   Verificar Health Check endpoint
   ```

3. **Memory Issues:**
   ```
   # Considerar upgrade de plan en Render
   # Optimizar queries de MongoDB
   # Revisar uso de caché
   ```

## 💰 Costos Estimados

### Render.com Pricing:
- **Free Tier**: $0/mes
  - 500 horas/mes
  - Duerme después de 15min inactividad
  - 512MB RAM

- **Starter**: $7/mes
  - Siempre activo
  - 512MB RAM
  - Custom domains

- **Standard**: $25/mes
  - 2GB RAM
  - Mejor rendimiento

### MongoDB Atlas:
- **M0 Free**: $0/mes (512MB)
- **M10 Basic**: $9/mes (2GB)

## 📞 Soporte

### Render.com:
- [Documentación](https://render.com/docs)
- [Community](https://community.render.com)
- [Status](https://status.render.com)

### MongoDB Atlas:
- [Documentación](https://docs.atlas.mongodb.com)
- [Support](https://support.mongodb.com)

---

¡Tu Task Manager API estará lista para producción en Render.com! 🚀