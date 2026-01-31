"""
Modelos Pydantic para Historial y Auditoría
Sistema de tracking de cambios en tareas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models import PyObjectId

class ActionType(str, Enum):
    """Tipos de acciones del historial - basado en sistema legacy"""
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    TITLE_CHANGED = "TITLE_CHANGED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    ASSIGNED = "ASSIGNED"
    UNASSIGNED = "UNASSIGNED"
    PROJECT_CHANGED = "PROJECT_CHANGED"
    DUE_DATE_CHANGED = "DUE_DATE_CHANGED"
    DESCRIPTION_CHANGED = "DESCRIPTION_CHANGED"
    HOURS_UPDATED = "HOURS_UPDATED"
    DELETED = "DELETED"

class HistoryBase(BaseModel):
    """Modelo base de entrada de historial"""
    task_id: PyObjectId = Field(..., description="ID de la tarea")
    action: ActionType = Field(..., description="Tipo de acción realizada")
    old_value: Optional[str] = Field(None, max_length=1000, description="Valor anterior")
    new_value: Optional[str] = Field(None, max_length=1000, description="Valor nuevo")
    details: Optional[str] = Field(None, max_length=500, description="Detalles adicionales")

class HistoryCreate(HistoryBase):
    """Modelo para crear entrada de historial"""
    pass

class HistoryResponse(BaseModel):
    """Modelo de respuesta de historial"""
    id: str
    task_id: str
    task_title: Optional[str] = None  # Poblado desde la base de datos
    action: ActionType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None
    user_id: str
    username: str  # Poblado desde la base de datos
    timestamp: datetime
    
    # Información contextual adicional
    project_name: Optional[str] = None  # Si la tarea tiene proyecto

class HistoryWithTask(HistoryResponse):
    """Historial con información completa de la tarea"""
    task_status: Optional[str] = None
    task_priority: Optional[str] = None
    task_assigned_username: Optional[str] = None

class HistoryInDB(BaseModel):
    """Modelo interno para la base de datos"""
    task_id: PyObjectId
    action: ActionType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    details: Optional[str] = None
    user_id: PyObjectId
    timestamp: datetime

class HistoryStats(BaseModel):
    """Estadísticas del historial"""
    total_actions: int = 0
    by_action_type: dict = {}
    by_user: dict = {}
    most_active_tasks: List[dict] = []
    recent_activity_count: int = 0  # Actividad en las últimas 24h