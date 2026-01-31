"""
FastAPI Task Manager - API Backend
Sistema de gestión de tareas con FastAPI y MongoDB
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import mongodb
from app.routers import auth, users, projects, tasks, comments, history, notifications, dashboard, admin
from app.middleware.logging_middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando Task Manager API...")
    await mongodb.connect()
    logger.info("Conexión a MongoDB establecida")
    yield
    # Shutdown
    logger.info("Cerrando Task Manager API...")
    await mongodb.disconnect()
    logger.info("Conexión a MongoDB cerrada")

# Crear instancia de FastAPI
app = FastAPI(
    title="Task Manager API",
    description="Sistema de gestión de tareas con FastAPI y MongoDB",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan
)

# Agregar middlewares en orden específico (el último agregado se ejecuta primero)
# 1. Rate Limiting (primero en ejecutarse)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Logging (después de security)
app.add_middleware(LoggingMiddleware, log_body=settings.debug)

# 4. CORS (último en agregarse, primero en la cadena)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(comments.router, prefix=settings.api_prefix)
app.include_router(history.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Task Manager API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "database": "connected" if mongodb.client else "disconnected"
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    db_status = "connected" if mongodb.client else "disconnected"
    return {
        "status": "healthy", 
        "message": "API is running",
        "database": db_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )