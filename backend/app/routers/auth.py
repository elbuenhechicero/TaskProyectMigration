"""
Router de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.core.config import settings
from app.core.database import get_database
from app.models.user import UserCreate, UserLogin, Token, UserResponse, UserInDB
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.dependencies import get_current_active_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db = Depends(get_database)):
    """Registrar nuevo usuario"""
    try:
        # Verificar si el usuario ya existe
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user.username},
                {"email": user.email}
            ]
        })
        
        if existing_user:
            if existing_user["username"] == user.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Crear usuario
        hashed_password = get_password_hash(user.password)
        user_doc = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        # Convertir a modelo de respuesta
        return UserResponse(
            id=str(result.inserted_id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user_doc["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log del error real
        print(f"Error creating user: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db = Depends(get_database)):
    """Login de usuario"""
    # Buscar usuario
    user_doc = await db.users.find_one({"username": user.username})
    
    if not user_doc or not verify_password(user.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Actualizar último login
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Crear token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": str(user_doc["_id"])},
        expires_delta=access_token_expires
    )
    
    # Crear respuesta de usuario
    user_response = UserResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        is_active=user_doc.get("is_active", True),
        is_admin=user_doc.get("is_admin", False),
        created_at=user_doc["created_at"],
        last_login=datetime.utcnow()
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """Obtener información del usuario actual"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )