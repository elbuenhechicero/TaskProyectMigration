"""
Modelos de tarea
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from app.models import BaseDocument, PyObjectId, TaskStatus, Priority

class TaskBase(BaseModel):
    """Modelo base de tarea"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    project_id: Optional[PyObjectId] = None
    assigned_to: Optional[PyObjectId] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)

class TaskCreate(TaskBase):
    """Modelo para crear tarea"""
    pass

class TaskUpdate(BaseModel):
    """Modelo para actualizar tarea"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    project_id: Optional[PyObjectId] = None
    assigned_to: Optional[PyObjectId] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)

class TaskInDB(BaseDocument):
    """Modelo de tarea en la base de datos"""
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    project_id: Optional[PyObjectId] = None
    assigned_to: Optional[PyObjectId] = None
    created_by: PyObjectId
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = 0
    actual_hours: Optional[float] = 0
    completed_at: Optional[datetime] = None
    
    # Campos para auditoría
    last_updated_by: Optional[PyObjectId] = None

class TaskResponse(BaseModel):
    """Modelo de respuesta de tarea"""
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: Priority
    project_id: Optional[str] = None
    project_name: Optional[str] = None  # Populated field
    assigned_to: Optional[str] = None
    assigned_user: Optional[str] = None  # Populated field (username)
    created_by: str
    creator_name: Optional[str] = None  # Populated field
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = 0
    actual_hours: Optional[float] = 0
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Status calculado
    is_overdue: bool = False
    days_until_due: Optional[int] = None

class TaskWithDetails(TaskResponse):
    """Tarea con detalles adicionales"""
    comments_count: int = 0
    history_count: int = 0
    tags: List[str] = []

class TaskSearch(BaseModel):
    """Modelo para búsqueda de tareas"""
    text: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    project_id: Optional[PyObjectId] = None
    assigned_to: Optional[PyObjectId] = None
    created_by: Optional[PyObjectId] = None
    due_date_from: Optional[date] = None
    due_date_to: Optional[date] = None
    is_overdue: Optional[bool] = None
    
    # Paginación
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)