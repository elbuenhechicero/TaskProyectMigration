"""
Router para gestión de comentarios
Sistema de colaboración en tareas con notificaciones de menciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import re
from app.core.database import get_database
from app.models.comment import CommentCreate, CommentUpdate, CommentResponse, CommentWithTask
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user
from app.utils.notification_service import NotificationService

router = APIRouter(prefix="/comments", tags=["Comments"])

def extract_mentions(content: str) -> List[str]:
    """Extraer menciones @username del contenido del comentario"""
    mention_pattern = r'@(\w+)'
    return re.findall(mention_pattern, content)

async def resolve_mentions(db, usernames: List[str]) -> List[ObjectId]:
    """Resolver usernames a ObjectIds"""
    if not usernames:
        return []
    
    users = await db.users.find({"username": {"$in": usernames}}).to_list(length=None)
    return [user["_id"] for user in users]

@router.get("/task/{task_id}", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: str,
    skip: int = Query(0, ge=0, description="Número de comentarios a omitir"),
    limit: int = Query(50, ge=1, le=100, description="Límite de comentarios a devolver"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener todos los comentarios de una tarea"""
    
    # Validar ObjectId de la tarea
    if not ObjectId.is_valid(task_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    
    # Verificar que la tarea existe
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Obtener comentarios ordenados por fecha de creación
    cursor = db.comments.find({"task_id": ObjectId(task_id)}).skip(skip).limit(limit).sort("created_at", 1)
    comments = await cursor.to_list(length=limit)
    
    # Procesar comentarios y poblar información
    comments_response = []
    for comment_doc in comments:
        # Obtener información del autor
        author = await db.users.find_one({"_id": comment_doc["author_id"]})
        author_username = author["username"] if author else "Unknown"
        
        # Extraer menciones
        mentions = extract_mentions(comment_doc["content"])
        
        # Verificar si fue editado
        is_edited = comment_doc["updated_at"] > comment_doc["created_at"]
        
        comments_response.append(CommentResponse(
            id=str(comment_doc["_id"]),
            content=comment_doc["content"],
            task_id=task_id,
            task_title=task["title"],
            author_id=str(comment_doc["author_id"]),
            author_username=author_username,
            created_at=comment_doc["created_at"],
            updated_at=comment_doc["updated_at"],
            is_edited=is_edited,
            mentions=mentions
        ))
    
    return comments_response

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Crear un nuevo comentario en una tarea"""
    
    # Verificar que la tarea existe
    task = await db.tasks.find_one({"_id": comment.task_id})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Extraer y resolver menciones
    mention_usernames = extract_mentions(comment.content)
    mention_ids = await resolve_mentions(db, mention_usernames)
    
    # Crear comentario
    comment_doc = {
        "content": comment.content,
        "task_id": comment.task_id,
        "author_id": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "mentions": mention_ids
    }
    
    result = await db.comments.insert_one(comment_doc)
    comment_doc["_id"] = result.inserted_id
    
    # Notificar menciones
    if mention_usernames:
        notification_service = NotificationService(db)
        await notification_service.notify_comment_mention(
            comment_id=result.inserted_id,
            task=task,
            mentioned_users=mention_usernames,
            author_user_id=current_user.id
        )
    
    return CommentResponse(
        id=str(result.inserted_id),
        content=comment.content,
        task_id=str(comment.task_id),
        task_title=task["title"],
        author_id=str(current_user.id),
        author_username=current_user.username,
        created_at=comment_doc["created_at"],
        updated_at=comment_doc["updated_at"],
        is_edited=False,
        mentions=mention_usernames
    )

@router.get("/{comment_id}", response_model=CommentWithTask)
async def get_comment(
    comment_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener un comentario específico con información de la tarea"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID format"
        )
    
    comment_doc = await db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Obtener información de la tarea
    task = await db.tasks.find_one({"_id": comment_doc["task_id"]})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated task not found"
        )
    
    # Obtener información del autor
    author = await db.users.find_one({"_id": comment_doc["author_id"]})
    author_username = author["username"] if author else "Unknown"
    
    # Obtener nombre del proyecto si existe
    project_name = None
    if task.get("project_id"):
        project = await db.projects.find_one({"_id": task["project_id"]})
        project_name = project["name"] if project else None
    
    # Extraer menciones y verificar si fue editado
    mentions = extract_mentions(comment_doc["content"])
    is_edited = comment_doc["updated_at"] > comment_doc["created_at"]
    
    return CommentWithTask(
        id=str(comment_doc["_id"]),
        content=comment_doc["content"],
        task_id=str(comment_doc["task_id"]),
        task_title=task["title"],
        task_status=task["status"],
        task_priority=task["priority"],
        project_name=project_name,
        author_id=str(comment_doc["author_id"]),
        author_username=author_username,
        created_at=comment_doc["created_at"],
        updated_at=comment_doc["updated_at"],
        is_edited=is_edited,
        mentions=mentions
    )

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Actualizar un comentario (solo el autor puede editarlo)"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID format"
        )
    
    # Verificar que el comentario existe
    comment_doc = await db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Solo el autor puede editar el comentario
    if str(comment_doc["author_id"]) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this comment"
        )
    
    # Extraer y resolver nuevas menciones
    mention_usernames = extract_mentions(comment_update.content)
    mention_ids = await resolve_mentions(db, mention_usernames)
    
    # Actualizar comentario
    update_data = {
        "content": comment_update.content,
        "updated_at": datetime.utcnow(),
        "mentions": mention_ids
    }
    
    await db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": update_data}
    )
    
    # Obtener comentario actualizado y información de la tarea
    updated_comment = await db.comments.find_one({"_id": ObjectId(comment_id)})
    task = await db.tasks.find_one({"_id": updated_comment["task_id"]})
    
    return CommentResponse(
        id=str(updated_comment["_id"]),
        content=updated_comment["content"],
        task_id=str(updated_comment["task_id"]),
        task_title=task["title"] if task else None,
        author_id=str(updated_comment["author_id"]),
        author_username=current_user.username,
        created_at=updated_comment["created_at"],
        updated_at=updated_comment["updated_at"],
        is_edited=True,
        mentions=mention_usernames
    )

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Eliminar un comentario (solo el autor o admin)"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID format"
        )
    
    # Verificar que el comentario existe
    comment_doc = await db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Solo el autor o admin pueden eliminar el comentario
    if str(comment_doc["author_id"]) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this comment"
        )
    
    # Eliminar comentario
    await db.comments.delete_one({"_id": ObjectId(comment_id)})
    
    return {"message": "Comment deleted successfully"}

@router.get("/user/{user_id}", response_model=List[CommentWithTask])
async def get_user_comments(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener todos los comentarios de un usuario específico"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Verificar que el usuario existe
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Solo admin o el mismo usuario pueden ver sus comentarios
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view user comments"
        )
    
    # Obtener comentarios del usuario
    cursor = db.comments.find({"author_id": ObjectId(user_id)}).skip(skip).limit(limit).sort("created_at", -1)
    comments = await cursor.to_list(length=limit)
    
    # Procesar comentarios con información de tareas
    comments_response = []
    for comment_doc in comments:
        # Obtener información de la tarea
        task = await db.tasks.find_one({"_id": comment_doc["task_id"]})
        if not task:  # Skip si la tarea fue eliminada
            continue
            
        # Obtener nombre del proyecto si existe
        project_name = None
        if task.get("project_id"):
            project = await db.projects.find_one({"_id": task["project_id"]})
            project_name = project["name"] if project else None
        
        # Extraer menciones y verificar si fue editado
        mentions = extract_mentions(comment_doc["content"])
        is_edited = comment_doc["updated_at"] > comment_doc["created_at"]
        
        comments_response.append(CommentWithTask(
            id=str(comment_doc["_id"]),
            content=comment_doc["content"],
            task_id=str(comment_doc["task_id"]),
            task_title=task["title"],
            task_status=task["status"],
            task_priority=task["priority"],
            project_name=project_name,
            author_id=str(comment_doc["author_id"]),
            author_username=user["username"],
            created_at=comment_doc["created_at"],
            updated_at=comment_doc["updated_at"],
            is_edited=is_edited,
            mentions=mentions
        ))
    
    return comments_response