"""
FastAPI Task Manager - API Backend
Sistema de gestión de tareas con FastAPI y MongoDB
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import mongodb
from app.routers import auth, users, projects, tasks, comments, history

# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await mongodb.connect()
    yield
    # Shutdown
    await mongodb.disconnect()

# Crear instancia de FastAPI
app = FastAPI(
    title="Task Manager API",
    description="Sistema de gestión de tareas con FastAPI y MongoDB",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan
)

# Configurar CORS
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