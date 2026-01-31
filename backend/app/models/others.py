"""
Modelos para comentarios, historial y notificaciones
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models import BaseDocument, PyObjectId, ActionType

# === COMENTARIOS ===
class CommentBase(BaseModel):
    """Modelo base de comentario"""
    text: str = Field(..., min_length=1, max_length=2000)

class CommentCreate(CommentBase):
    """Modelo para crear comentario"""
    task_id: PyObjectId

class CommentInDB(BaseDocument):
    """Modelo de comentario en la base de datos"""
    task_id: PyObjectId
    user_id: PyObjectId
    text: str
    
    # Campos opcionales para edición
    is_edited: bool = False
    edited_at: Optional[datetime] = None

class CommentResponse(BaseModel):
    """Modelo de respuesta de comentario"""
    id: str
    task_id: str
    user_id: str
    username: str  # Populated field
    text: str
    is_edited: bool = False
    edited_at: Optional[datetime] = None
    created_at: datetime

# === HISTORIAL/AUDITORÍA ===
class HistoryCreate(BaseModel):
    """Modelo para crear entrada de historial"""
    task_id: PyObjectId
    action: ActionType
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None

class HistoryInDB(BaseDocument):
    """Modelo de historial en la base de datos"""
    task_id: PyObjectId
    user_id: PyObjectId
    action: ActionType
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HistoryResponse(BaseModel):
    """Modelo de respuesta de historial"""
    id: str
    task_id: str
    user_id: str
    username: str  # Populated field
    action: ActionType
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime

# === NOTIFICACIONES ===
class NotificationBase(BaseModel):
    """Modelo base de notificación"""
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    type: str = "info"  # info, warning, error, success

class NotificationCreate(NotificationBase):
    """Modelo para crear notificación"""
    user_id: PyObjectId
    task_id: Optional[PyObjectId] = None
    project_id: Optional[PyObjectId] = None

class NotificationInDB(BaseDocument):
    """Modelo de notificación en la base de datos"""
    user_id: PyObjectId
    title: str
    message: str
    type: str = "info"
    read: bool = False
    read_at: Optional[datetime] = None
    
    # Referencias opcionales
    task_id: Optional[PyObjectId] = None
    project_id: Optional[PyObjectId] = None
    
    # Metadata
    data: Optional[dict] = {}

class NotificationResponse(BaseModel):
    """Modelo de respuesta de notificación"""
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool
    read_at: Optional[datetime] = None
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    data: Optional[dict] = {}
    created_at: datetime

class NotificationUpdate(BaseModel):
    """Modelo para actualizar notificación"""
    read: bool = True