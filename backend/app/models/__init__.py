"""
Modelos Pydantic para el sistema de gestión de tareas
Basados en el sistema legacy JavaScript
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

# Custom ObjectId type for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "format": "objectid"}

# Enums para estados y prioridades
class TaskStatus(str, Enum):
    PENDING = "Pendiente"
    IN_PROGRESS = "En Progreso" 
    COMPLETED = "Completada"
    BLOCKED = "Bloqueada"
    CANCELLED = "Cancelada"

class Priority(str, Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Crítica"

class ActionType(str, Enum):
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

# Base model with common fields
class BaseDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )