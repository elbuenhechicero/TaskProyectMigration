"""
Task Manager API - Punto de entrada principal
Sistema de gestión de tareas con FastAPI y MongoDB
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configuración de la aplicación
app = FastAPI(
    title="Task Manager API",
    description="Sistema de gestión de tareas moderno",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
origins = [
    "http://localhost:3000",
    "https://localhost:3000", 
    "https://taskmanager-frontend.onrender.com",
    "https://*.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Task Manager API",
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Task Manager API",
        "version": "1.0.0"
    }

# Endpoint básico de prueba
@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "API funcionando correctamente",
        "endpoints_available": [
            "/docs - Documentación interactiva",
            "/health - Health check",
            "/api/v1/auth/* - Autenticación",
            "/api/v1/tasks/* - Gestión de tareas",
            "/api/v1/projects/* - Gestión de proyectos"
        ]
    }

# Aquí agregarías tus routers cuando tengas el código completo
# from app.routers import auth, tasks, projects, etc.
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        access_log=True,
        log_level="info"
    )