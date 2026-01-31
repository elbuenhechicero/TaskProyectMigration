"""
Servicio de Notificaciones Automáticas
Genera notificaciones basadas en eventos del sistema como asignaciones de tareas, menciones, etc.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.notification import NotificationType

class NotificationService:
    def __init__(self, database):
        self.db = database
    
    async def create_notification(
        self,
        user_id: ObjectId,
        message: str,
        notification_type: NotificationType,
        task_id: Optional[ObjectId] = None,
        project_id: Optional[ObjectId] = None,
        comment_id: Optional[ObjectId] = None,
        created_by: Optional[ObjectId] = None,
        priority: str = "normal",
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Crear una notificación en la base de datos"""
        
        notification = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "read": False,
            "created_at": datetime.utcnow(),
            "task_id": task_id,
            "project_id": project_id,
            "comment_id": comment_id,
            "priority": priority,
            "created_by": created_by,
            "expires_at": expires_at
        }
        
        result = await self.db.notifications.insert_one(notification)
        notification["_id"] = result.inserted_id
        return notification
    
    async def notify_task_assigned(
        self,
        task: Dict[str, Any],
        assigned_by_user_id: ObjectId
    ):
        """Notificar asignación de tarea"""
        
        if not task.get("assigned_to") or str(task["assigned_to"]) == str(assigned_by_user_id):
            return  # No notificar si no hay asignado o es auto-asignación
        
        # Obtener información del usuario que asigna
        assigned_by = await self.db.users.find_one({"_id": assigned_by_user_id})
        assigned_by_name = assigned_by["username"] if assigned_by else "Unknown"
        
        message = f"{assigned_by_name} te asignó la tarea: {task['title']}"
        
        await self.create_notification(
            user_id=task["assigned_to"],
            message=message,
            notification_type=NotificationType.TASK_ASSIGNED,
            task_id=task["_id"],
            project_id=task.get("project_id"),
            created_by=assigned_by_user_id,
            priority="normal"
        )
    
    async def notify_task_updated(
        self,
        task: Dict[str, Any],
        updated_by_user_id: ObjectId,
        changes: List[str]
    ):
        """Notificar actualización de tarea"""
        
        # Si no está asignada o se actualizó por el mismo usuario asignado, no notificar
        if not task.get("assigned_to") or str(task["assigned_to"]) == str(updated_by_user_id):
            return
        
        # Obtener información del usuario que actualiza
        updated_by = await self.db.users.find_one({"_id": updated_by_user_id})
        updated_by_name = updated_by["username"] if updated_by else "Unknown"
        
        # Crear mensaje descriptivo de los cambios
        change_description = ", ".join(changes) if changes else "información"
        message = f"{updated_by_name} actualizó {change_description} en la tarea: {task['title']}"
        
        await self.create_notification(
            user_id=task["assigned_to"],
            message=message,
            notification_type=NotificationType.TASK_UPDATED,
            task_id=task["_id"],
            project_id=task.get("project_id"),
            created_by=updated_by_user_id,
            priority="normal"
        )
    
    async def notify_task_completed(
        self,
        task: Dict[str, Any],
        completed_by_user_id: ObjectId
    ):
        """Notificar finalización de tarea al creador del proyecto si es diferente"""
        
        if not task.get("project_id"):
            return
        
        # Obtener el proyecto para notificar al creador
        project = await self.db.projects.find_one({"_id": task["project_id"]})
        if not project or str(project["created_by"]) == str(completed_by_user_id):
            return
        
        # Obtener información del usuario que completó
        completed_by = await self.db.users.find_one({"_id": completed_by_user_id})
        completed_by_name = completed_by["username"] if completed_by else "Unknown"
        
        message = f"{completed_by_name} completó la tarea '{task['title']}' en el proyecto {project['name']}"
        
        await self.create_notification(
            user_id=project["created_by"],
            message=message,
            notification_type=NotificationType.TASK_COMPLETED,
            task_id=task["_id"],
            project_id=task["project_id"],
            created_by=completed_by_user_id,
            priority="normal"
        )
    
    async def notify_comment_mention(
        self,
        comment_id: ObjectId,
        task: Dict[str, Any],
        mentioned_users: List[str],
        author_user_id: ObjectId
    ):
        """Notificar menciones en comentarios"""
        
        # Obtener información del autor
        author = await self.db.users.find_one({"_id": author_user_id})
        author_name = author["username"] if author else "Unknown"
        
        # Obtener IDs de usuarios mencionados
        mentioned_user_docs = await self.db.users.find(
            {"username": {"$in": mentioned_users}}
        ).to_list(length=None)
        
        for user_doc in mentioned_user_docs:
            # No notificar al autor del comentario
            if str(user_doc["_id"]) == str(author_user_id):
                continue
            
            message = f"{author_name} te mencionó en un comentario de la tarea: {task['title']}"
            
            await self.create_notification(
                user_id=user_doc["_id"],
                message=message,
                notification_type=NotificationType.COMMENT_MENTION,
                task_id=task["_id"],
                project_id=task.get("project_id"),
                comment_id=comment_id,
                created_by=author_user_id,
                priority="normal"
            )
    
    async def notify_due_date_approaching(
        self,
        task: Dict[str, Any]
    ):
        """Notificar que se aproxima fecha límite (ejecutar vía cron job)"""
        
        if not task.get("assigned_to") or not task.get("due_date"):
            return
        
        due_date = task["due_date"]
        now = datetime.utcnow()
        
        # Notificar 24 horas antes
        time_diff = due_date - now
        if timedelta(hours=20) <= time_diff <= timedelta(hours=24):
            message = f"La tarea '{task['title']}' vence mañana"
            
            await self.create_notification(
                user_id=task["assigned_to"],
                message=message,
                notification_type=NotificationType.DUE_DATE_APPROACHING,
                task_id=task["_id"],
                project_id=task.get("project_id"),
                priority="high",
                expires_at=due_date + timedelta(days=1)
            )
    
    async def notify_project_update(
        self,
        project: Dict[str, Any],
        updated_by_user_id: ObjectId,
        notification_message: str
    ):
        """Notificar actualización de proyecto a todos los miembros"""
        
        # Obtener todos los usuarios que tienen tareas en este proyecto
        tasks_cursor = self.db.tasks.find(
            {"project_id": project["_id"], "assigned_to": {"$ne": None}}
        )
        tasks = await tasks_cursor.to_list(length=None)
        
        # Crear set de usuarios únicos a notificar
        users_to_notify = set()
        for task in tasks:
            if task.get("assigned_to") and str(task["assigned_to"]) != str(updated_by_user_id):
                users_to_notify.add(task["assigned_to"])
        
        # Obtener información del usuario que actualiza
        updated_by = await self.db.users.find_one({"_id": updated_by_user_id})
        updated_by_name = updated_by["username"] if updated_by else "Unknown"
        
        # Crear notificaciones
        for user_id in users_to_notify:
            message = f"{updated_by_name} actualizó el proyecto '{project['name']}': {notification_message}"
            
            await self.create_notification(
                user_id=user_id,
                message=message,
                notification_type=NotificationType.PROJECT_UPDATE,
                project_id=project["_id"],
                created_by=updated_by_user_id,
                priority="normal"
            )
    
    async def notify_project_deadline(
        self,
        project: Dict[str, Any]
    ):
        """Notificar fecha límite de proyecto (ejecutar vía cron job)"""
        
        if not project.get("end_date"):
            return
        
        end_date = project["end_date"]
        now = datetime.utcnow()
        
        # Notificar 3 días antes
        time_diff = end_date - now
        if timedelta(days=2.5) <= time_diff <= timedelta(days=3):
            
            # Obtener todos los usuarios del proyecto
            tasks_cursor = self.db.tasks.find(
                {"project_id": project["_id"], "assigned_to": {"$ne": None}}
            )
            tasks = await tasks_cursor.to_list(length=None)
            
            users_to_notify = set()
            for task in tasks:
                if task.get("assigned_to"):
                    users_to_notify.add(task["assigned_to"])
            
            # Agregar creador del proyecto
            users_to_notify.add(project["created_by"])
            
            # Crear notificaciones
            for user_id in users_to_notify:
                message = f"El proyecto '{project['name']}' termina en 3 días"
                
                await self.create_notification(
                    user_id=user_id,
                    message=message,
                    notification_type=NotificationType.PROJECT_DEADLINE,
                    project_id=project["_id"],
                    priority="high",
                    expires_at=end_date + timedelta(days=1)
                )
    
    async def cleanup_expired_notifications(self):
        """Limpiar notificaciones expiradas (ejecutar vía cron job)"""
        
        result = await self.db.notifications.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
    
    async def cleanup_old_notifications(self, days_to_keep: int = 30):
        """Limpiar notificaciones antiguas ya leídas (ejecutar vía cron job)"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        result = await self.db.notifications.delete_many({
            "read": True,
            "created_at": {"$lt": cutoff_date}
        })
        
        return result.deleted_count