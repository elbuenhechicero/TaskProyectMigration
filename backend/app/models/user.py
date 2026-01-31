"""
Modelos de usuario
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import BaseDocument, PyObjectId

class UserBase(BaseModel):
    """Modelo base de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserInDB(BaseDocument):
    """Modelo de usuario en la base de datos"""
    username: str
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    last_login: Optional[datetime] = None

class UserResponse(BaseModel):
    """Modelo de respuesta de usuario (sin password)"""
    id: str
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    """Modelo para login"""
    username: str
    password: str

class Token(BaseModel):
    """Modelo para token de acceso"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse