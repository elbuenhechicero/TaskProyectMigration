"""
Modelos Pydantic para Comentarios
Sistema de colaboración en tareas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import PyObjectId

class CommentBase(BaseModel):
    """Modelo base de comentario"""
    content: str = Field(..., min_length=1, max_length=2000)
    task_id: PyObjectId = Field(..., description="ID de la tarea")

class CommentCreate(CommentBase):
    """Modelo para crear comentario"""
    pass

class CommentUpdate(BaseModel):
    """Modelo para actualizar comentario"""
    content: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(BaseModel):
    """Modelo de respuesta de comentario"""
    id: str
    content: str
    task_id: str
    task_title: Optional[str] = None  # Poblado desde la base de datos
    author_id: str
    author_username: str  # Poblado desde la base de datos
    created_at: datetime
    updated_at: datetime
    is_edited: bool = False  # True si fue editado después de crear
    mentions: List[str] = []  # Usernames mencionados en el comentario

class CommentWithTask(CommentResponse):
    """Comentario con información completa de la tarea"""
    task_status: Optional[str] = None
    task_priority: Optional[str] = None
    project_name: Optional[str] = None

class CommentInDB(BaseModel):
    """Modelo interno para la base de datos"""
    content: str
    task_id: PyObjectId
    author_id: PyObjectId
    created_at: datetime
    updated_at: datetime
    mentions: List[PyObjectId] = []  # ObjectIds de usuarios mencionados