"""
Router para gestión de tareas (CRUD completo)
El core del sistema de gestión de tareas con notificaciones automáticas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date
from app.core.database import get_database
from app.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskInDB, TaskWithDetails
from app.models import TaskStatus, Priority
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user
from app.utils.history import HistoryTracker
from app.utils.notification_service import NotificationService
from app.utils.cache import CacheInvalidationService

def convert_datetime_to_date(dt):
    """Convertir datetime a date para la respuesta de la API"""
    if dt and isinstance(dt, datetime):
        return dt.date()
    return dt

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0, description="Número de tareas a omitir"),
    limit: int = Query(50, ge=1, le=100, description="Límite de tareas a devolver"),
    status: Optional[TaskStatus] = Query(None, description="Filtrar por estado"),
    priority: Optional[Priority] = Query(None, description="Filtrar por prioridad"),
    project_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    assigned_to: Optional[str] = Query(None, description="Filtrar por usuario asignado"),
    overdue: Optional[bool] = Query(None, description="Filtrar tareas vencidas"),
    search: Optional[str] = Query(None, description="Buscar en título y descripción"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Listar tareas con filtros avanzados"""
    
    # Construir filtros
    filter_query = {}
    
    if status:
        filter_query["status"] = status
    
    if priority:
        filter_query["priority"] = priority
    
    if project_id:
        if not ObjectId.is_valid(project_id):
            raise HTTPException(status_code=400, detail="Invalid project ID")
        filter_query["project_id"] = ObjectId(project_id)
    
    if assigned_to:
        if not ObjectId.is_valid(assigned_to):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        filter_query["assigned_to"] = ObjectId(assigned_to)
    
    if search:
        filter_query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Filtro para tareas vencidas
    if overdue is True:
        filter_query["due_date"] = {"$lt": datetime.utcnow()}
        filter_query["status"] = {"$ne": TaskStatus.COMPLETED}
    
    # Obtener tareas
    cursor = db.tasks.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
    tasks = await cursor.to_list(length=limit)
    
    # Convertir a response models con datos poblados
    tasks_response = []
    for task_doc in tasks:
        # Obtener nombre del proyecto
        project_name = None
        if task_doc.get("project_id"):
            project = await db.projects.find_one({"_id": task_doc["project_id"]})
            project_name = project["name"] if project else None
        
        # Obtener nombre del usuario asignado
        assigned_username = None
        if task_doc.get("assigned_to"):
            user = await db.users.find_one({"_id": task_doc["assigned_to"]})
            assigned_username = user["username"] if user else None
        
        # Obtener nombre del creador
        created_username = None
        if task_doc.get("created_by"):
            creator = await db.users.find_one({"_id": task_doc["created_by"]})
            created_username = creator["username"] if creator else None
        
        # Verificar si está vencida
        is_overdue = False
        if task_doc.get("due_date") and task_doc["status"] != TaskStatus.COMPLETED:
            is_overdue = task_doc["due_date"] < datetime.utcnow()
        
        tasks_response.append(TaskResponse(
            id=str(task_doc["_id"]),
            title=task_doc["title"],
            description=task_doc.get("description"),
            status=task_doc["status"],
            priority=task_doc["priority"],
            project_id=str(task_doc["project_id"]) if task_doc.get("project_id") else None,
            project_name=project_name,
            assigned_to=str(task_doc["assigned_to"]) if task_doc.get("assigned_to") else None,
            assigned_username=assigned_username,
            due_date=convert_datetime_to_date(task_doc.get("due_date")),
            estimated_hours=task_doc.get("estimated_hours", 0.0),
            actual_hours=task_doc.get("actual_hours", 0.0),
            created_by=str(task_doc["created_by"]),
            created_username=created_username,
            created_at=task_doc["created_at"],
            updated_at=task_doc["updated_at"],
            is_overdue=is_overdue
        ))
    
    return tasks_response

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Crear nueva tarea"""
    
    # Validar proyecto si se especifica
    if task.project_id:
        project = await db.projects.find_one({"_id": task.project_id})
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Validar usuario asignado si se especifica
    assigned_username = None
    if task.assigned_to:
        assigned_user = await db.users.find_one({"_id": task.assigned_to})
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )
        assigned_username = assigned_user["username"]
    
    # Crear tarea
    task_doc = {
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "due_date": datetime.combine(task.due_date, datetime.min.time()) if task.due_date else None,
        "estimated_hours": task.estimated_hours or 0.0,
        "actual_hours": 0.0,
        "created_by": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.tasks.insert_one(task_doc)
    task_doc["_id"] = result.inserted_id
    
    # Log creación en historial
    await HistoryTracker.log_task_created(
        task_id=result.inserted_id,
        user_id=current_user.id, 
        task_title=task.title
    )
    
    # Notificar asignación de tarea si hay un usuario asignado
    if task.assigned_to:
        notification_service = NotificationService(db)
        await notification_service.notify_task_assigned(
            task=task_doc,
            assigned_by_user_id=current_user.id
        )
    
    # Invalidar caché relacionado
    CacheInvalidationService.invalidate_task_caches(
        task_id=str(result.inserted_id),
        project_id=str(task.project_id) if task.project_id else None
    )
    
    # Obtener nombres para la respuesta
    project_name = None
    if task.project_id:
        project = await db.projects.find_one({"_id": task.project_id})
        project_name = project["name"] if project else None
    
    return TaskResponse(
        id=str(result.inserted_id),
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        project_id=str(task.project_id) if task.project_id else None,
        project_name=project_name,
        assigned_to=str(task.assigned_to) if task.assigned_to else None,
        assigned_username=assigned_username,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours or 0.0,
        actual_hours=0.0,
        created_by=str(current_user.id),
        created_username=current_user.username,
        created_at=task_doc["created_at"],
        updated_at=task_doc["updated_at"],
        is_overdue=False
    )

@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener una tarea específica con detalles completos"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    
    task_doc = await db.tasks.find_one({"_id": ObjectId(task_id)})
    
    if not task_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Obtener datos relacionados
    project_name = None
    if task_doc.get("project_id"):
        project = await db.projects.find_one({"_id": task_doc["project_id"]})
        project_name = project["name"] if project else None
    
    assigned_username = None
    if task_doc.get("assigned_to"):
        user = await db.users.find_one({"_id": task_doc["assigned_to"]})
        assigned_username = user["username"] if user else None
    
    created_username = None
    if task_doc.get("created_by"):
        creator = await db.users.find_one({"_id": task_doc["created_by"]})
        created_username = creator["username"] if creator else None
    
    # Contar comentarios e historial
    comments_count = await db.comments.count_documents({"task_id": ObjectId(task_id)})
    history_count = await db.history.count_documents({"task_id": ObjectId(task_id)})
    
    # Calcular porcentaje de progreso
    progress_percentage = 0.0
    if task_doc.get("estimated_hours", 0) > 0:
        progress_percentage = (task_doc.get("actual_hours", 0) / task_doc["estimated_hours"]) * 100
        progress_percentage = min(progress_percentage, 100.0)  # Cap at 100%
    
    # Verificar si está vencida
    is_overdue = False
    if task_doc.get("due_date") and task_doc["status"] != TaskStatus.COMPLETED:
        is_overdue = task_doc["due_date"] < datetime.utcnow()
    
    return TaskWithDetails(
        id=str(task_doc["_id"]),
        title=task_doc["title"],
        description=task_doc.get("description"),
        status=task_doc["status"],
        priority=task_doc["priority"],
        project_id=str(task_doc["project_id"]) if task_doc.get("project_id") else None,
        project_name=project_name,
        assigned_to=str(task_doc["assigned_to"]) if task_doc.get("assigned_to") else None,
        assigned_username=assigned_username,
        due_date=convert_datetime_to_date(task_doc.get("due_date")),
        estimated_hours=task_doc.get("estimated_hours", 0.0),
        actual_hours=task_doc.get("actual_hours", 0.0),
        created_by=str(task_doc["created_by"]),
        created_username=created_username,
        created_at=task_doc["created_at"],
        updated_at=task_doc["updated_at"],
        is_overdue=is_overdue,
        comments_count=comments_count,
        history_count=history_count,
        progress_percentage=round(progress_percentage, 1)
    )

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Actualizar una tarea"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    
    # Verificar que la tarea existe
    existing_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Solo el creador, asignado o admin puede actualizar la tarea
    if (not current_user.is_admin and 
        str(existing_task["created_by"]) != str(current_user.id) and
        str(existing_task.get("assigned_to", "")) != str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this task"
        )
    
    # Construir update data
    update_data = {"updated_at": datetime.utcnow()}
    
    if task_update.title is not None:
        update_data["title"] = task_update.title
    
    if task_update.description is not None:
        update_data["description"] = task_update.description
    
    if task_update.status is not None:
        update_data["status"] = task_update.status
    
    if task_update.priority is not None:
        update_data["priority"] = task_update.priority
    
    if task_update.project_id is not None:
        if task_update.project_id:
            # Verificar que el proyecto existe
            project = await db.projects.find_one({"_id": task_update.project_id})
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
        update_data["project_id"] = task_update.project_id
    
    if task_update.assigned_to is not None:
        if task_update.assigned_to:
            # Verificar que el usuario existe
            user = await db.users.find_one({"_id": task_update.assigned_to})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )
        update_data["assigned_to"] = task_update.assigned_to
    
    if task_update.due_date is not None:
        update_data["due_date"] = datetime.combine(task_update.due_date, datetime.min.time()) if task_update.due_date else None
    
    if task_update.estimated_hours is not None:
        update_data["estimated_hours"] = task_update.estimated_hours
    
    if task_update.actual_hours is not None:
        update_data["actual_hours"] = task_update.actual_hours
    
    # Actualizar tarea
    await db.tasks.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": update_data}
    )
    
    # Log cambios en historial
    await HistoryTracker.log_task_updated(
        task_id=ObjectId(task_id),
        user_id=current_user.id,
        old_task=existing_task,
        new_task={**existing_task, **update_data}
    )
    
    # Obtener tarea actualizada para notificaciones
    updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    
    # Notificar cambios en la tarea
    notification_service = NotificationService(db)
    
    # Verificar cambios importantes para notificar
    changes = []
    if task_update.assigned_to is not None and task_update.assigned_to != existing_task.get("assigned_to"):
        # Nueva asignación
        if task_update.assigned_to:
            await notification_service.notify_task_assigned(
                task=updated_task,
                assigned_by_user_id=current_user.id
            )
        changes.append("asignación")
    
    if task_update.status is not None and task_update.status != existing_task.get("status"):
        changes.append("estado")
        # Notificar finalización
        if task_update.status == TaskStatus.COMPLETED:
            await notification_service.notify_task_completed(
                task=updated_task,
                completed_by_user_id=current_user.id
            )
    
    if task_update.priority is not None and task_update.priority != existing_task.get("priority"):
        changes.append("prioridad")
    
    if task_update.due_date is not None and task_update.due_date != convert_datetime_to_date(existing_task.get("due_date")):
        changes.append("fecha límite")
        
    if task_update.title is not None and task_update.title != existing_task.get("title"):
        changes.append("título")
    
    # Notificar actualizaciones si hay cambios importantes
    if changes:
        await notification_service.notify_task_updated(
            task=updated_task,
            updated_by_user_id=current_user.id,
            changes=changes
        )
        
        # Invalidar caché relacionado
        CacheInvalidationService.invalidate_task_caches(
            task_id=task_id,
            project_id=str(updated_task["project_id"]) if updated_task.get("project_id") else None
        )
    assigned_username = None
    if updated_task.get("assigned_to"):
        user = await db.users.find_one({"_id": updated_task["assigned_to"]})
        assigned_username = user["username"] if user else None
    
    created_username = None
    if updated_task.get("created_by"):
        creator = await db.users.find_one({"_id": updated_task["created_by"]})
        created_username = creator["username"] if creator else None
    
    is_overdue = False
    if updated_task.get("due_date") and updated_task["status"] != TaskStatus.COMPLETED:
        is_overdue = updated_task["due_date"] < datetime.utcnow()
    
    return TaskResponse(
        id=str(updated_task["_id"]),
        title=updated_task["title"],
        description=updated_task.get("description"),
        status=updated_task["status"],
        priority=updated_task["priority"],
        project_id=str(updated_task["project_id"]) if updated_task.get("project_id") else None,
        project_name=project_name,
        assigned_to=str(updated_task["assigned_to"]) if updated_task.get("assigned_to") else None,
        assigned_username=assigned_username,
        due_date=convert_datetime_to_date(updated_task.get("due_date")),
        estimated_hours=updated_task.get("estimated_hours", 0.0),
        actual_hours=updated_task.get("actual_hours", 0.0),
        created_by=str(updated_task["created_by"]),
        created_username=created_username,
        created_at=updated_task["created_at"],
        updated_at=updated_task["updated_at"],
        is_overdue=is_overdue
    )

@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Eliminar una tarea"""
    
    # Validar ObjectId
    if not ObjectId.is_valid(task_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    
    # Verificar que la tarea existe
    task_doc = await db.tasks.find_one({"_id": ObjectId(task_id)})
    if not task_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Solo el creador o admin puede eliminar la tarea
    if not current_user.is_admin and str(task_doc["created_by"]) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this task"
        )
    
    # Log eliminación en historial antes de borrar
    await HistoryTracker.log_task_deleted(
        task_id=ObjectId(task_id),
        user_id=current_user.id,
        task_title=task_doc["title"]
    )
    
    # Eliminar comentarios e historial relacionado
    await db.comments.delete_many({"task_id": ObjectId(task_id)})
    await db.notifications.delete_many({"task_id": ObjectId(task_id)})
    
    # Eliminar tarea
    await db.tasks.delete_one({"_id": ObjectId(task_id)})
    
    return {"message": f"Task '{task_doc['title']}' and related data deleted successfully"}

@router.get("/stats/summary")
async def get_tasks_stats(
    project_id: Optional[str] = Query(None, description="Filtrar estadísticas por proyecto"),
    assigned_to: Optional[str] = Query(None, description="Filtrar estadísticas por usuario asignado"),
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas de tareas"""
    
    # Construir filtro base
    match_filter = {}
    
    if project_id:
        if not ObjectId.is_valid(project_id):
            raise HTTPException(status_code=400, detail="Invalid project ID")
        match_filter["project_id"] = ObjectId(project_id)
    
    if assigned_to:
        if not ObjectId.is_valid(assigned_to):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        match_filter["assigned_to"] = ObjectId(assigned_to)
    
    # Pipeline de agregación
    pipeline = [
        {"$match": match_filter},
        {
            "$group": {
                "_id": None,
                "total_tasks": {"$sum": 1},
                "by_status": {
                    "$push": "$status"
                },
                "by_priority": {
                    "$push": "$priority"
                },
                "total_estimated_hours": {"$sum": "$estimated_hours"},
                "total_actual_hours": {"$sum": "$actual_hours"},
                "overdue_count": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$ne": ["$status", "Completada"]},
                                    {"$lt": ["$due_date", datetime.utcnow()]}
                                ]
                            },
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]
    
    result = await db.tasks.aggregate(pipeline).to_list(length=1)
    
    if not result:
        return {
            "total_tasks": 0,
            "by_status": {},
            "by_priority": {},
            "overdue_tasks": 0,
            "completion_rate": 0.0,
            "total_estimated_hours": 0.0,
            "total_actual_hours": 0.0,
            "efficiency_rate": 0.0
        }
    
    stats = result[0]
    
    # Procesar estadísticas por estado
    status_counts = {}
    for status in stats["by_status"]:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Procesar estadísticas por prioridad
    priority_counts = {}
    for priority in stats["by_priority"]:
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Calcular tasa de completitud
    completed_tasks = status_counts.get("Completada", 0)
    completion_rate = (completed_tasks / stats["total_tasks"] * 100) if stats["total_tasks"] > 0 else 0.0
    
    # Calcular eficiencia (actual vs estimado)
    efficiency_rate = 0.0
    if stats["total_estimated_hours"] > 0:
        efficiency_rate = (stats["total_estimated_hours"] / stats["total_actual_hours"] * 100)
        if stats["total_actual_hours"] == 0:
            efficiency_rate = 100.0
    
    return {
        "total_tasks": stats["total_tasks"],
        "by_status": status_counts,
        "by_priority": priority_counts,
        "overdue_tasks": stats["overdue_count"],
        "completion_rate": round(completion_rate, 2),
        "total_estimated_hours": stats["total_estimated_hours"],
        "total_actual_hours": stats["total_actual_hours"],
        "efficiency_rate": round(efficiency_rate, 2)
    }