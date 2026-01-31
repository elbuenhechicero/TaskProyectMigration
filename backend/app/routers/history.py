"""
Router para gestión de historial y auditoría
Sistema de tracking de cambios en tareas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from app.core.database import get_database
from app.models.history import (
    HistoryCreate, HistoryResponse, HistoryWithTask, 
    HistoryStats, ActionType
)
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/history", tags=["History"])

async def log_history_entry(
    db,
    task_id: ObjectId,
    action: ActionType,
    user_id: ObjectId,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    details: Optional[str] = None
):
    """Función helper para registrar entradas de historial"""
    history_doc = {
        "task_id": task_id,
        "action": action,
        "old_value": old_value,
        "new_value": new_value,
        "details": details,
        "user_id": user_id,
        "timestamp": datetime.utcnow()
    }
    
    await db.history.insert_one(history_doc)
    return history_doc

@router.get("/task/{task_id}", response_model=List[HistoryResponse])
async def get_task_history(
    task_id: str,
    skip: int = Query(0, ge=0, description="Número de entradas a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Límite de entradas a devolver"),
    action_type: Optional[ActionType] = Query(None, description="Filtrar por tipo de acción"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener historial completo de una tarea específica"""
    
    # Validar ObjectId
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
    
    # Construir filtros
    filter_query = {"task_id": ObjectId(task_id)}
    if action_type:
        filter_query["action"] = action_type
    
    # Obtener historial ordenado por timestamp descendente (más reciente primero)
    cursor = db.history.find(filter_query).skip(skip).limit(limit).sort("timestamp", -1)
    history_entries = await cursor.to_list(length=limit)
    
    # Procesar entradas y poblar información
    history_response = []
    for entry in history_entries:
        # Obtener información del usuario
        user = await db.users.find_one({"_id": entry["user_id"]})
        username = user["username"] if user else "Unknown"
        
        # Obtener información del proyecto si existe
        project_name = None
        if task.get("project_id"):
            project = await db.projects.find_one({"_id": task["project_id"]})
            project_name = project["name"] if project else None
        
        history_response.append(HistoryResponse(
            id=str(entry["_id"]),
            task_id=task_id,
            task_title=task["title"],
            action=entry["action"],
            old_value=entry.get("old_value"),
            new_value=entry.get("new_value"),
            details=entry.get("details"),
            user_id=str(entry["user_id"]),
            username=username,
            timestamp=entry["timestamp"],
            project_name=project_name
        ))
    
    return history_response

@router.get("/", response_model=List[HistoryWithTask])
async def get_all_history(
    skip: int = Query(0, ge=0, description="Número de entradas a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Límite de entradas a devolver"),
    action_type: Optional[ActionType] = Query(None, description="Filtrar por tipo de acción"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    hours_ago: Optional[int] = Query(None, ge=1, le=168, description="Filtrar últimas X horas"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener historial general de todo el sistema"""
    
    # Solo admin puede ver historial completo
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view system history"
        )
    
    # Construir filtros
    filter_query = {}
    
    if action_type:
        filter_query["action"] = action_type
    
    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        filter_query["user_id"] = ObjectId(user_id)
    
    if hours_ago:
        since_time = datetime.utcnow() - timedelta(hours=hours_ago)
        filter_query["timestamp"] = {"$gte": since_time}
    
    # Obtener historial
    cursor = db.history.find(filter_query).skip(skip).limit(limit).sort("timestamp", -1)
    history_entries = await cursor.to_list(length=limit)
    
    # Procesar entradas con información completa
    history_response = []
    for entry in history_entries:
        # Obtener información de la tarea
        task = await db.tasks.find_one({"_id": entry["task_id"]})
        if not task:  # Skip si la tarea fue eliminada
            continue
        
        # Obtener información del usuario
        user = await db.users.find_one({"_id": entry["user_id"]})
        username = user["username"] if user else "Unknown"
        
        # Obtener información del proyecto
        project_name = None
        if task.get("project_id"):
            project = await db.projects.find_one({"_id": task["project_id"]})
            project_name = project["name"] if project else None
        
        # Obtener información del usuario asignado a la tarea
        task_assigned_username = None
        if task.get("assigned_to"):
            assigned_user = await db.users.find_one({"_id": task["assigned_to"]})
            task_assigned_username = assigned_user["username"] if assigned_user else None
        
        history_response.append(HistoryWithTask(
            id=str(entry["_id"]),
            task_id=str(entry["task_id"]),
            task_title=task["title"],
            task_status=task["status"],
            task_priority=task["priority"],
            task_assigned_username=task_assigned_username,
            action=entry["action"],
            old_value=entry.get("old_value"),
            new_value=entry.get("new_value"),
            details=entry.get("details"),
            user_id=str(entry["user_id"]),
            username=username,
            timestamp=entry["timestamp"],
            project_name=project_name
        ))
    
    return history_response

@router.get("/user/{user_id}", response_model=List[HistoryWithTask])
async def get_user_history(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener historial de acciones de un usuario específico"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Solo admin o el mismo usuario pueden ver su historial
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view user history"
        )
    
    # Verificar que el usuario existe
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Obtener historial del usuario
    cursor = db.history.find({"user_id": ObjectId(user_id)}).skip(skip).limit(limit).sort("timestamp", -1)
    history_entries = await cursor.to_list(length=limit)
    
    # Procesar entradas con información de tareas
    history_response = []
    for entry in history_entries:
        # Obtener información de la tarea
        task = await db.tasks.find_one({"_id": entry["task_id"]})
        if not task:  # Skip si la tarea fue eliminada
            continue
        
        # Obtener información del proyecto
        project_name = None
        if task.get("project_id"):
            project = await db.projects.find_one({"_id": task["project_id"]})
            project_name = project["name"] if project else None
        
        # Usuario asignado a la tarea
        task_assigned_username = None
        if task.get("assigned_to"):
            assigned_user = await db.users.find_one({"_id": task["assigned_to"]})
            task_assigned_username = assigned_user["username"] if assigned_user else None
        
        history_response.append(HistoryWithTask(
            id=str(entry["_id"]),
            task_id=str(entry["task_id"]),
            task_title=task["title"],
            task_status=task["status"],
            task_priority=task["priority"],
            task_assigned_username=task_assigned_username,
            action=entry["action"],
            old_value=entry.get("old_value"),
            new_value=entry.get("new_value"),
            details=entry.get("details"),
            user_id=str(entry["user_id"]),
            username=user["username"],
            timestamp=entry["timestamp"],
            project_name=project_name
        ))
    
    return history_response

@router.get("/stats/summary", response_model=HistoryStats)
async def get_history_stats(
    days_ago: int = Query(30, ge=1, le=365, description="Días hacia atrás para estadísticas"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas del historial del sistema"""
    
    # Solo admin puede ver estadísticas
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to view history statistics"
        )
    
    # Filtro de tiempo
    since_time = datetime.utcnow() - timedelta(days=days_ago)
    filter_query = {"timestamp": {"$gte": since_time}}
    
    # Pipeline de agregación para estadísticas
    pipeline = [
        {"$match": filter_query},
        {
            "$group": {
                "_id": None,
                "total_actions": {"$sum": 1},
                "by_action": {"$push": "$action"},
                "by_user": {"$push": "$user_id"},
                "by_task": {"$push": "$task_id"},
                "recent_activity": {
                    "$sum": {
                        "$cond": [
                            {"$gte": ["$timestamp", datetime.utcnow() - timedelta(hours=24)]},
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]
    
    result = await db.history.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return HistoryStats()
    
    stats = result[0]
    
    # Procesar estadísticas por tipo de acción
    by_action_type = {}
    for action in stats["by_action"]:
        by_action_type[action] = by_action_type.get(action, 0) + 1
    
    # Procesar estadísticas por usuario
    by_user = {}
    for user_id in stats["by_user"]:
        by_user[str(user_id)] = by_user.get(str(user_id), 0) + 1
    
    # Obtener nombres de usuarios para las estadísticas
    user_stats = {}
    for user_id_str, count in by_user.items():
        user = await db.users.find_one({"_id": ObjectId(user_id_str)})
        username = user["username"] if user else "Unknown"
        user_stats[username] = count
    
    # Procesar tareas más activas
    task_activity = {}
    for task_id in stats["by_task"]:
        task_activity[str(task_id)] = task_activity.get(str(task_id), 0) + 1
    
    # Obtener las 5 tareas más activas
    most_active_tasks = []
    for task_id_str, count in sorted(task_activity.items(), key=lambda x: x[1], reverse=True)[:5]:
        task = await db.tasks.find_one({"_id": ObjectId(task_id_str)})
        if task:
            most_active_tasks.append({
                "task_id": task_id_str,
                "task_title": task["title"],
                "activity_count": count
            })
    
    return HistoryStats(
        total_actions=stats["total_actions"],
        by_action_type=by_action_type,
        by_user=user_stats,
        most_active_tasks=most_active_tasks,
        recent_activity_count=stats["recent_activity"]
    )