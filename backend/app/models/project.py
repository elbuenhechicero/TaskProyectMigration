"""
Modelos de proyecto
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import BaseDocument, PyObjectId

class ProjectBase(BaseModel):
    """Modelo base de proyecto"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class ProjectCreate(ProjectBase):
    """Modelo para crear proyecto"""
    pass

class ProjectUpdate(BaseModel):
    """Modelo para actualizar proyecto"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class ProjectInDB(BaseDocument):
    """Modelo de proyecto en la base de datos"""
    name: str
    description: Optional[str] = None
    created_by: PyObjectId
    task_count: int = 0  # Cache del número de tareas

class ProjectResponse(BaseModel):
    """Modelo de respuesta de proyecto"""
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

class ProjectWithStats(ProjectResponse):
    """Proyecto con estadísticas"""
    tasks_by_status: dict = {}  # {"Pendiente": 5, "Completada": 3}
    completion_rate: float = 0.0  # Porcentaje de tareas completadas