"""
Utilidades de seguridad para autenticación JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

def _safe_truncate_password(password: str) -> bytes:
    """Trunca contraseña de forma segura para bcrypt y devuelve bytes"""
    # Convertir a bytes
    password_bytes = password.encode('utf-8')
    
    # Si está dentro del límite, devolverlo
    if len(password_bytes) <= 72:
        return password_bytes
    
    # Truncar a exactamente 72 bytes
    return password_bytes[:72]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password plano contra hash usando bcrypt directo"""
    try:
        # Preparar contraseña
        password_bytes = _safe_truncate_password(plain_password)
        
        # Convertir hash de string a bytes si es necesario
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
            
        # Verificar con bcrypt directo
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Generar hash de password usando bcrypt directo"""
    try:
        # Preparar contraseña
        password_bytes = _safe_truncate_password(password)
        
        # Generar salt y hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Devolver como string
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verificar token JWT y obtener username"""
    try:
        # Asegurarse de que no tenga el prefijo "Bearer "
        if token.startswith("Bearer "):
            token = token[7:]  # Remover "Bearer "
            
        print(f"Clean token length: {len(token)}")
        print(f"Clean token starts: {token[:50]}")
        print(f"Using SECRET_KEY: {settings.secret_key[:20]}...")
        print(f"Algorithm: {settings.algorithm}")
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        
        print(f"Token payload: {payload}")
        print(f"Extracted username: {username}")
        
        if username is None:
            print("Username is None in payload")
            return None
        return username
    except JWTError as e:
        print(f"JWT Error: {e}")
        print(f"JWT Error type: {type(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error in verify_token: {e}")
        return None

def decode_token(token: str) -> Optional[dict]:
    """Decodificar token JWT y obtener payload completo"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None