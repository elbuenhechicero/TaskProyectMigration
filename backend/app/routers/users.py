"""
Router para gestión de usuarios (CRUD completo)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.core.database import get_database
from app.models.user import UserCreate, UserUpdate, UserResponse, UserInDB
from app.utils.dependencies import get_current_active_user, get_current_admin_user
from app.utils.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Número de usuarios a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Límite de usuarios a devolver"),
    search: Optional[str] = Query(None, description="Buscar por username o email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por usuarios activos"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Listar usuarios con paginación y filtros"""
    
    # Construir filtros
    filter_query = {}
    
    if search:
        filter_query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"full_name": {"$regex": search, "$options": "i"}}
        ]
    
    if is_active is not None:
        filter_query["is_active"] = is_active
    
    # Obtener usuarios
    cursor = db.users.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    users = await cursor.to_list(length=limit)
    
    # Convertir a response models
    users_response = []
    for user_doc in users:
        users_response.append(UserResponse(
            id=str(user_doc["_id"]),
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            is_active=user_doc.get("is_active", True),
            is_admin=user_doc.get("is_admin", False),
            created_at=user_doc["created_at"],
            last_login=user_doc.get("last_login")
        ))
    
    return users_response

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener un usuario por ID"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Solo admin puede ver otros usuarios, o el usuario puede verse a sí mismo
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        is_active=user_doc.get("is_active", True),
        is_admin=user_doc.get("is_admin", False),
        created_at=user_doc["created_at"],
        last_login=user_doc.get("last_login")
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Actualizar un usuario"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Solo admin puede actualizar otros usuarios, o el usuario puede actualizarse a sí mismo
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Solo admin puede cambiar is_admin
    if not current_user.is_admin and user_update.is_admin is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify admin privileges"
        )
    
    # Verificar que el usuario existe
    existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Construir update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if user_update.username is not None:
        # Verificar que el username no existe
        existing_username = await db.users.find_one({
            "username": user_update.username,
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        update_data["username"] = user_update.username
    
    if user_update.email is not None:
        # Verificar que el email no existe
        existing_email = await db.users.find_one({
            "email": user_update.email,
            "_id": {"$ne": ObjectId(user_id)}
        })
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        update_data["email"] = user_update.email
    
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active
    
    if user_update.is_admin is not None and current_user.is_admin:
        update_data["is_admin"] = user_update.is_admin
    
    # Actualizar usuario
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    # Obtener usuario actualizado
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    
    return UserResponse(
        id=str(updated_user["_id"]),
        username=updated_user["username"],
        email=updated_user["email"],
        full_name=updated_user.get("full_name"),
        is_active=updated_user.get("is_active", True),
        is_admin=updated_user.get("is_admin", False),
        created_at=updated_user["created_at"],
        last_login=updated_user.get("last_login")
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_admin_user),  # Solo admin
    db = Depends(get_database)
):
    """Eliminar un usuario (solo admin)"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # No se puede eliminar a sí mismo
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Verificar que el usuario existe
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # En lugar de eliminar, desactivar el usuario (soft delete)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "is_active": False,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": f"User {user_doc['username']} deactivated successfully"}

@router.get("/stats/summary")
async def get_users_stats(
    current_user: UserInDB = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Obtener estadísticas de usuarios (solo admin)"""
    
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_users": {"$sum": 1},
                "active_users": {
                    "$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}
                },
                "admin_users": {
                    "$sum": {"$cond": [{"$eq": ["$is_admin", True]}, 1, 0]}
                }
            }
        }
    ]
    
    result = await db.users.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return {
            "total_users": 0,
            "active_users": 0,
            "admin_users": 0,
            "inactive_users": 0
        }
    
    stats = result[0]
    stats["inactive_users"] = stats["total_users"] - stats["active_users"]
    del stats["_id"]
    
    return stats