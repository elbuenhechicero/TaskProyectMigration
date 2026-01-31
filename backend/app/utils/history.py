"""
Utilidades para el sistema de historial y auditoría
Tracking automático de cambios en tareas
"""
from typing import Optional, Any, Dict
from bson import ObjectId
from datetime import datetime
from app.models.history import ActionType
from app.core.database import get_database

class HistoryTracker:
    """Clase para facilitar el tracking de cambios"""
    
    @staticmethod
    async def log_task_created(task_id: ObjectId, user_id: ObjectId, task_title: str):
        """Log creación de tarea"""
        db = await get_database()
        await db.history.insert_one({
            "task_id": task_id,
            "action": ActionType.CREATED,
            "old_value": None,
            "new_value": task_title,
            "details": "Task created",
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        })
    
    @staticmethod
    async def log_task_updated(
        task_id: ObjectId, 
        user_id: ObjectId, 
        old_task: Dict[str, Any], 
        new_task: Dict[str, Any]
    ):
        """Log actualización de tarea con detección automática de cambios"""
        db = await get_database()
        
        # Detectar y loguear cambios específicos
        changes = []
        
        # Título
        if old_task.get("title") != new_task.get("title"):
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.TITLE_CHANGED,
                "old_value": old_task.get("title", ""),
                "new_value": new_task.get("title", ""),
                "details": "Title updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("title")
        
        # Estado
        if old_task.get("status") != new_task.get("status"):
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.STATUS_CHANGED,
                "old_value": old_task.get("status", ""),
                "new_value": new_task.get("status", ""),
                "details": "Status updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("status")
        
        # Prioridad
        if old_task.get("priority") != new_task.get("priority"):
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.PRIORITY_CHANGED,
                "old_value": old_task.get("priority", ""),
                "new_value": new_task.get("priority", ""),
                "details": "Priority updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("priority")
        
        # Usuario asignado
        old_assigned = old_task.get("assigned_to")
        new_assigned = new_task.get("assigned_to")
        if old_assigned != new_assigned:
            if new_assigned and not old_assigned:
                # Asignación nueva
                assigned_user = await db.users.find_one({"_id": new_assigned})
                username = assigned_user["username"] if assigned_user else "Unknown"
                await db.history.insert_one({
                    "task_id": task_id,
                    "action": ActionType.ASSIGNED,
                    "old_value": "Unassigned",
                    "new_value": username,
                    "details": f"Task assigned to {username}",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow()
                })
                changes.append("assigned")
            elif old_assigned and not new_assigned:
                # Desasignación
                old_user = await db.users.find_one({"_id": old_assigned})
                old_username = old_user["username"] if old_user else "Unknown"
                await db.history.insert_one({
                    "task_id": task_id,
                    "action": ActionType.UNASSIGNED,
                    "old_value": old_username,
                    "new_value": "Unassigned",
                    "details": f"Task unassigned from {old_username}",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow()
                })
                changes.append("unassigned")
            elif old_assigned != new_assigned:
                # Reasignación
                old_user = await db.users.find_one({"_id": old_assigned})
                new_user = await db.users.find_one({"_id": new_assigned})
                old_username = old_user["username"] if old_user else "Unknown"
                new_username = new_user["username"] if new_user else "Unknown"
                await db.history.insert_one({
                    "task_id": task_id,
                    "action": ActionType.ASSIGNED,
                    "old_value": old_username,
                    "new_value": new_username,
                    "details": f"Task reassigned from {old_username} to {new_username}",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow()
                })
                changes.append("reassigned")
        
        # Proyecto
        if old_task.get("project_id") != new_task.get("project_id"):
            old_project = None
            new_project = None
            
            if old_task.get("project_id"):
                old_proj_doc = await db.projects.find_one({"_id": old_task["project_id"]})
                old_project = old_proj_doc["name"] if old_proj_doc else "Unknown"
            
            if new_task.get("project_id"):
                new_proj_doc = await db.projects.find_one({"_id": new_task["project_id"]})
                new_project = new_proj_doc["name"] if new_proj_doc else "Unknown"
            
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.PROJECT_CHANGED,
                "old_value": old_project or "No project",
                "new_value": new_project or "No project",
                "details": "Project changed",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("project")
        
        # Fecha de vencimiento
        old_due = old_task.get("due_date")
        new_due = new_task.get("due_date")
        if old_due != new_due:
            # Convertir datetime a string para comparación
            old_due_str = old_due.strftime("%Y-%m-%d") if old_due else "No due date"
            new_due_str = new_due.strftime("%Y-%m-%d") if new_due else "No due date"
            
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.DUE_DATE_CHANGED,
                "old_value": old_due_str,
                "new_value": new_due_str,
                "details": "Due date updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("due_date")
        
        # Descripción
        if old_task.get("description") != new_task.get("description"):
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.DESCRIPTION_CHANGED,
                "old_value": (old_task.get("description", "")[:100] + "..." if len(old_task.get("description", "")) > 100 else old_task.get("description", "")),
                "new_value": (new_task.get("description", "")[:100] + "..." if len(new_task.get("description", "")) > 100 else new_task.get("description", "")),
                "details": "Description updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("description")
        
        # Horas (estimadas o reales)
        if (old_task.get("estimated_hours", 0) != new_task.get("estimated_hours", 0) or 
            old_task.get("actual_hours", 0) != new_task.get("actual_hours", 0)):
            
            old_hours = f"Est: {old_task.get('estimated_hours', 0)}h, Act: {old_task.get('actual_hours', 0)}h"
            new_hours = f"Est: {new_task.get('estimated_hours', 0)}h, Act: {new_task.get('actual_hours', 0)}h"
            
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.HOURS_UPDATED,
                "old_value": old_hours,
                "new_value": new_hours,
                "details": "Hours updated",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
            changes.append("hours")
        
        # Log genérico si hubo cambios
        if changes:
            await db.history.insert_one({
                "task_id": task_id,
                "action": ActionType.UPDATED,
                "old_value": None,
                "new_value": None,
                "details": f"Task updated: {', '.join(changes)}",
                "user_id": user_id,
                "timestamp": datetime.utcnow()
            })
    
    @staticmethod
    async def log_task_deleted(task_id: ObjectId, user_id: ObjectId, task_title: str):
        """Log eliminación de tarea"""
        db = await get_database()
        await db.history.insert_one({
            "task_id": task_id,
            "action": ActionType.DELETED,
            "old_value": task_title,
            "new_value": None,
            "details": "Task deleted",
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        })
    
    @staticmethod
    async def log_custom_action(
        task_id: ObjectId,
        user_id: ObjectId,
        action: ActionType,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        details: Optional[str] = None
    ):
        """Log acción personalizada"""
        db = await get_database()
        await db.history.insert_one({
            "task_id": task_id,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "details": details,
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        })