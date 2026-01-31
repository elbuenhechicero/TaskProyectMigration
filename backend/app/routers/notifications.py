"""
Router para Sistema de Notificaciones
Basado en la funcionalidad del sistema legacy
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from app.core.database import get_database
from app.models.notification import (
    NotificationCreate, NotificationResponse, NotificationWithDetails,
    NotificationStats, NotificationType, BulkNotificationCreate
)
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    skip: int = Query(0, ge=0, description="Número de notificaciones a omitir"),
    limit: int = Query(50, ge=1, le=100, description="Límite de notificaciones a devolver"),
    unread_only: bool = Query(False, description="Solo notificaciones no leídas"),
    notification_type: Optional[NotificationType] = Query(None, description="Filtrar por tipo"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener notificaciones del usuario actual"""
    
    # Construir filtros
    filter_query = {"user_id": current_user.id}
    
    if unread_only:
        filter_query["read"] = False
    
    if notification_type:
        filter_query["type"] = notification_type
    
    # Filtrar notificaciones no expiradas
    filter_query["$or"] = [
        {"expires_at": None},
        {"expires_at": {"$gte": datetime.utcnow()}}
    ]
    
    # Obtener notificaciones ordenadas por fecha (más recientes primero)
    cursor = db.notifications.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    notifications = await cursor.to_list(length=limit)
    
    # Procesar notificaciones y poblar información
    notifications_response = []
    for notif in notifications:
        # Información de tarea si aplica
        task_title = None
        if notif.get("task_id"):
            task = await db.tasks.find_one({"_id": notif["task_id"]})
            task_title = task["title"] if task else None
        
        # Información de proyecto si aplica
        project_name = None
        if notif.get("project_id"):
            project = await db.projects.find_one({"_id": notif["project_id"]})
            project_name = project["name"] if project else None
        
        notifications_response.append(NotificationResponse(
            id=str(notif["_id"]),
            user_id=str(notif["user_id"]),
            username=current_user.username,
            message=notif["message"],
            type=notif["type"],
            read=notif.get("read", False),
            created_at=notif["created_at"],
            task_id=str(notif["task_id"]) if notif.get("task_id") else None,
            task_title=task_title,
            project_id=str(notif["project_id"]) if notif.get("project_id") else None,
            project_name=project_name,
            comment_id=str(notif["comment_id"]) if notif.get("comment_id") else None,
            priority=notif.get("priority", "normal"),
            expires_at=notif.get("expires_at")
        ))
    
    return notifications_response

@router.get("/{notification_id}", response_model=NotificationWithDetails)
async def get_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener una notificación específica con detalles completos"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format"
        )
    
    notification = await db.notifications.find_one({"_id": ObjectId(notification_id)})
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Verificar que la notificación pertenece al usuario actual
    if str(notification["user_id"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this notification"
        )
    
    # Obtener información detallada de la tarea si aplica
    task_info = {}
    if notification.get("task_id"):
        task = await db.tasks.find_one({"_id": notification["task_id"]})
        if task:
            task_info = {
                "task_title": task["title"],
                "task_status": task["status"],
                "task_priority": task["priority"],
                "task_due_date": task.get("due_date")
            }
    
    # Información del proyecto
    project_name = None
    if notification.get("project_id"):
        project = await db.projects.find_one({"_id": notification["project_id"]})
        project_name = project["name"] if project else None
    
    # Información de quién creó la notificación
    assigned_by_username = None
    if notification.get("created_by"):
        creator = await db.users.find_one({"_id": notification["created_by"]})
        assigned_by_username = creator["username"] if creator else None
    
    return NotificationWithDetails(
        id=str(notification["_id"]),
        user_id=str(notification["user_id"]),
        username=current_user.username,
        message=notification["message"],
        type=notification["type"],
        read=notification.get("read", False),
        created_at=notification["created_at"],
        task_id=str(notification["task_id"]) if notification.get("task_id") else None,
        project_id=str(notification["project_id"]) if notification.get("project_id") else None,
        project_name=project_name,
        comment_id=str(notification["comment_id"]) if notification.get("comment_id") else None,
        priority=notification.get("priority", "normal"),
        expires_at=notification.get("expires_at"),
        assigned_by_username=assigned_by_username,
        **task_info
    )

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Crear una nueva notificación (solo admin)"""
    
    # Solo admin puede crear notificaciones manuales
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to create notifications"
        )
    
    # Validar que el usuario destinatario existe
    user = await db.users.find_one({"_id": notification.user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found"
        )
    
    # Validar referencias opcionales
    if notification.task_id:
        task = await db.tasks.find_one({"_id": notification.task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
    
    if notification.project_id:
        project = await db.projects.find_one({"_id": notification.project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Crear notificación
    notification_doc = {
        "user_id": notification.user_id,
        "message": notification.message,
        "type": notification.type,
        "read": False,
        "created_at": datetime.utcnow(),
        "task_id": notification.task_id,
        "project_id": notification.project_id,
        "comment_id": notification.comment_id,
        "priority": "normal",
        "created_by": current_user.id
    }
    
    result = await db.notifications.insert_one(notification_doc)
    
    return NotificationResponse(
        id=str(result.inserted_id),
        user_id=str(notification.user_id),
        username=user["username"],
        message=notification.message,
        type=notification.type,
        read=False,
        created_at=notification_doc["created_at"],
        task_id=str(notification.task_id) if notification.task_id else None,
        project_id=str(notification.project_id) if notification.project_id else None,
        comment_id=str(notification.comment_id) if notification.comment_id else None,
        priority="normal"
    )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Marcar una notificación como leída"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format"
        )
    
    # Verificar que la notificación existe y pertenece al usuario
    notification = await db.notifications.find_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user.id
    })
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Marcar como leída
    await db.notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"read": True}}
    )
    
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
async def mark_all_notifications_read(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Marcar todas las notificaciones del usuario como leídas"""
    
    result = await db.notifications.update_many(
        {"user_id": current_user.id, "read": False},
        {"$set": {"read": True}}
    )
    
    return {"message": f"{result.modified_count} notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Eliminar una notificación"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format"
        )
    
    # Verificar que la notificación existe y pertenece al usuario
    notification = await db.notifications.find_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user.id
    })
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Eliminar notificación
    await db.notifications.delete_one({"_id": ObjectId(notification_id)})
    
    return {"message": "Notification deleted successfully"}

@router.get("/stats/summary", response_model=NotificationStats)
async def get_notification_stats(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas de notificaciones del usuario"""
    
    # Pipeline de agregación para estadísticas
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {
            "$group": {
                "_id": None,
                "total_notifications": {"$sum": 1},
                "unread_count": {
                    "$sum": {"$cond": [{"$eq": ["$read", False]}, 1, 0]}
                },
                "by_type": {"$push": "$type"},
                "recent_count": {
                    "$sum": {
                        "$cond": [
                            {"$gte": ["$created_at", datetime.utcnow() - timedelta(hours=24)]},
                            1,
                            0
                        ]
                    }
                },
                "high_priority_count": {
                    "$sum": {"$cond": [{"$eq": ["$priority", "high"]}, 1, 0]}
                }
            }
        }
    ]
    
    result = await db.notifications.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return NotificationStats()
    
    stats = result[0]
    
    # Procesar estadísticas por tipo
    by_type = {}
    for notif_type in stats["by_type"]:
        by_type[notif_type] = by_type.get(notif_type, 0) + 1
    
    return NotificationStats(
        total_notifications=stats["total_notifications"],
        unread_count=stats["unread_count"],
        by_type=by_type,
        recent_count=stats["recent_count"],
        high_priority_count=stats["high_priority_count"]
    )

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_bulk_notifications(
    bulk_notification: BulkNotificationCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Crear notificaciones masivas (solo admin)"""
    
    # Solo admin puede crear notificaciones masivas
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for bulk notifications"
        )
    
    # Validar que todos los usuarios existen
    users = await db.users.find({"_id": {"$in": bulk_notification.user_ids}}).to_list(length=None)
    if len(users) != len(bulk_notification.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some target users not found"
        )
    
    # Crear notificaciones
    notifications = []
    current_time = datetime.utcnow()
    
    for user_id in bulk_notification.user_ids:
        notifications.append({
            "user_id": user_id,
            "message": bulk_notification.message,
            "type": bulk_notification.type,
            "read": False,
            "created_at": current_time,
            "task_id": bulk_notification.task_id,
            "project_id": bulk_notification.project_id,
            "priority": bulk_notification.priority,
            "created_by": current_user.id
        })
    
    if notifications:
        result = await db.notifications.insert_many(notifications)
        return {"message": f"Created {len(result.inserted_ids)} notifications"}
    
    return {"message": "No notifications created"}