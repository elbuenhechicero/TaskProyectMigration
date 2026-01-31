"""
Dependencias de FastAPI para autenticación
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.security import verify_token, decode_token
from app.core.database import get_database
from app.models.user import UserInDB
from bson import ObjectId

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_database)
) -> UserInDB:
    """Obtener usuario actual desde token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        username = verify_token(credentials.credentials)
        if username is None:
            raise credentials_exception
        
        # Buscar usuario en la base de datos
        user_doc = await db.users.find_one({"username": username})
        if user_doc is None:
            raise credentials_exception
            
        # Convertir documento a modelo Pydantic
        user = UserInDB(**user_doc)
        return user
        
    except Exception as e:
        raise credentials_exception

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Obtener usuario actual activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """Obtener usuario admin actual"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """Autenticación opcional - devuelve username si hay token válido"""
    if credentials is None:
        return None
    
    username = verify_token(credentials.credentials)
    return username