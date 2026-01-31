"""
Modelos Pydantic para Sistema de Notificaciones
Basado en el sistema legacy JavaScript
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.models import PyObjectId

class NotificationType(str, Enum):
    """Tipos de notificaciones - compatibles con sistema legacy"""
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    TASK_DUE_SOON = "task_due_soon"
    COMMENT_MENTION = "comment_mention"
    COMMENT_ADDED = "comment_added"
    PROJECT_ASSIGNED = "project_assigned"
    SYSTEM_ANNOUNCEMENT = "system_announcement"

class NotificationBase(BaseModel):
    """Modelo base de notificación"""
    user_id: PyObjectId = Field(..., description="ID del usuario destinatario")
    message: str = Field(..., min_length=1, max_length=500)
    type: NotificationType = Field(..., description="Tipo de notificación")
    task_id: Optional[PyObjectId] = Field(None, description="ID de la tarea relacionada")
    project_id: Optional[PyObjectId] = Field(None, description="ID del proyecto relacionado") 
    comment_id: Optional[PyObjectId] = Field(None, description="ID del comentario relacionado")

class NotificationCreate(NotificationBase):
    """Modelo para crear notificación"""
    pass

class NotificationResponse(BaseModel):
    """Modelo de respuesta de notificación"""
    id: str
    user_id: str
    username: str  # Poblado desde la base de datos
    message: str
    type: NotificationType
    read: bool = False
    created_at: datetime
    
    # Información contextual poblada
    task_id: Optional[str] = None
    task_title: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    comment_id: Optional[str] = None
    
    # Metadatos adicionales
    priority: str = "normal"  # normal, high, urgent
    expires_at: Optional[datetime] = None

class NotificationWithDetails(NotificationResponse):
    """Notificación con información completa"""
    task_status: Optional[str] = None
    task_priority: Optional[str] = None
    task_due_date: Optional[datetime] = None
    assigned_by_username: Optional[str] = None  # Quién realizó la acción

class NotificationInDB(BaseModel):
    """Modelo interno para la base de datos"""
    user_id: PyObjectId
    message: str
    type: NotificationType
    read: bool = False
    created_at: datetime
    task_id: Optional[PyObjectId] = None
    project_id: Optional[PyObjectId] = None
    comment_id: Optional[PyObjectId] = None
    priority: str = "normal"
    expires_at: Optional[datetime] = None
    created_by: Optional[PyObjectId] = None  # Usuario que generó la notificación

class NotificationStats(BaseModel):
    """Estadísticas de notificaciones para un usuario"""
    total_notifications: int = 0
    unread_count: int = 0
    by_type: dict = {}
    recent_count: int = 0  # Últimas 24h
    high_priority_count: int = 0

class BulkNotificationCreate(BaseModel):
    """Para crear notificaciones masivas"""
    user_ids: List[PyObjectId]
    message: str = Field(..., min_length=1, max_length=500)
    type: NotificationType
    task_id: Optional[PyObjectId] = None
    project_id: Optional[PyObjectId] = None
    priority: str = "normal"