"""
Script para poblar la base de datos con datos de prueba
Para demostrar el funcionamiento del sistema de dashboard y reportes
"""
import asyncio
from datetime import datetime, timedelta, date
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.models import TaskStatus, Priority
from app.utils.security import get_password_hash
import random

settings = Settings()

async def populate_database():
    """Poblar la base de datos con datos de ejemplo"""
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    
    print("🚀 Iniciando población de datos de prueba...")
    
    # Limpiar datos existentes (opcional)
    # await db.users.delete_many({})
    # await db.projects.delete_many({})
    # await db.tasks.delete_many({})
    # await db.comments.delete_many({})
    
    # Crear usuarios de prueba
    users_data = [
        {
            "_id": ObjectId(),
            "username": "admin",
            "email": "admin@taskmanager.com",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True,
            "is_admin": True,
            "created_at": datetime.utcnow() - timedelta(days=60),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "username": "juan_dev",
            "email": "juan@example.com",
            "hashed_password": get_password_hash("password123"),
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow() - timedelta(days=45),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "username": "maria_pm",
            "email": "maria@example.com", 
            "hashed_password": get_password_hash("password123"),
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow() - timedelta(days=40),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "username": "carlos_qa",
            "email": "carlos@example.com",
            "hashed_password": get_password_hash("password123"),
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Insertar usuarios solo si no existen
    for user_data in users_data:
        existing = await db.users.find_one({"username": user_data["username"]})
        if not existing:
            await db.users.insert_one(user_data)
            print(f"✅ Usuario creado: {user_data['username']}")
        else:
            # Actualizar el ID para usar en proyectos/tareas
            user_data["_id"] = existing["_id"]
            print(f"ℹ️  Usuario ya existe: {user_data['username']}")
    
    # Crear proyectos de prueba
    projects_data = [
        {
            "_id": ObjectId(),
            "name": "Sistema de Gestión de Tareas",
            "description": "Desarrollo de una aplicación web para gestión de tareas y proyectos",
            "status": "active",
            "created_by": users_data[1]["_id"],  # juan_dev
            "created_at": datetime.utcnow() - timedelta(days=35),
            "updated_at": datetime.utcnow() - timedelta(days=2),
            "start_date": datetime.utcnow() - timedelta(days=35),
            "end_date": datetime.utcnow() + timedelta(days=30)
        },
        {
            "_id": ObjectId(),
            "name": "API de Notificaciones",
            "description": "Sistema de notificaciones en tiempo real para usuarios",
            "status": "active",
            "created_by": users_data[2]["_id"],  # maria_pm
            "created_at": datetime.utcnow() - timedelta(days=25),
            "updated_at": datetime.utcnow() - timedelta(days=1),
            "start_date": datetime.utcnow() - timedelta(days=25),
            "end_date": datetime.utcnow() + timedelta(days=15)
        },
        {
            "_id": ObjectId(),
            "name": "Dashboard Analytics",
            "description": "Dashboard con métricas y reportes de productividad",
            "status": "completed",
            "created_by": users_data[0]["_id"],  # admin
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=5),
            "start_date": datetime.utcnow() - timedelta(days=20),
            "end_date": datetime.utcnow() - timedelta(days=5)
        }
    ]
    
    # Insertar proyectos
    for project_data in projects_data:
        existing = await db.projects.find_one({"name": project_data["name"]})
        if not existing:
            await db.projects.insert_one(project_data)
            print(f"✅ Proyecto creado: {project_data['name']}")
        else:
            project_data["_id"] = existing["_id"]
            print(f"ℹ️  Proyecto ya existe: {project_data['name']}")
    
    # Crear tareas de prueba con variedad de estados y fechas
    tasks_data = []
    task_titles = [
        "Diseñar base de datos",
        "Implementar autenticación JWT",
        "Crear API REST de usuarios",
        "Desarrollar sistema de comentarios", 
        "Implementar notificaciones push",
        "Crear dashboard de métricas",
        "Configurar CI/CD pipeline",
        "Escribir documentación de API",
        "Realizar pruebas de carga",
        "Implementar cache Redis",
        "Optimizar consultas SQL",
        "Crear sistema de reportes",
        "Implementar export CSV",
        "Configurar monitoreo",
        "Revisar seguridad API",
        "Actualizar dependencias",
        "Corregir bugs críticos",
        "Mejorar UX del dashboard",
        "Implementar búsqueda avanzada",
        "Crear backup automatizado"
    ]
    
    statuses = [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]
    priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH]
    
    for i, title in enumerate(task_titles):
        # Distribuir tareas entre proyectos
        project = projects_data[i % len(projects_data)]
        
        # Distribuir entre usuarios (excluyendo admin)
        assigned_user = users_data[(i % 3) + 1]
        
        # Crear fechas variadas
        created_days_ago = random.randint(1, 30)
        due_days_from_now = random.randint(-5, 20)  # Algunas vencidas
        
        # Estado basado en fecha de creación (más antiguas más posibles de estar completadas)
        if created_days_ago > 20:
            status = random.choices(statuses, weights=[10, 20, 70])[0]  # Más completadas
        elif created_days_ago > 10:
            status = random.choices(statuses, weights=[30, 50, 20])[0]  # Mixto
        else:
            status = random.choices(statuses, weights=[60, 30, 10])[0]  # Más pendientes
        
        # Si está completada, actualizar fecha de actualización
        updated_at = datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago))
        if status == TaskStatus.COMPLETED:
            updated_at = datetime.utcnow() - timedelta(days=random.randint(0, created_days_ago // 2))
        
        task = {
            "_id": ObjectId(),
            "title": title,
            "description": f"Descripción detallada para la tarea: {title}",
            "status": status,
            "priority": random.choice(priorities),
            "project_id": project["_id"],
            "assigned_to": assigned_user["_id"],
            "created_by": project["created_by"],
            "created_at": datetime.utcnow() - timedelta(days=created_days_ago),
            "updated_at": updated_at,
            "due_date": datetime.utcnow() + timedelta(days=due_days_from_now),
            "estimated_hours": random.uniform(2, 40),
            "actual_hours": random.uniform(1, 35) if status == TaskStatus.COMPLETED else random.uniform(0, 10)
        }
        
        tasks_data.append(task)
    
    # Insertar tareas
    for task_data in tasks_data:
        existing = await db.tasks.find_one({"title": task_data["title"]})
        if not existing:
            await db.tasks.insert_one(task_data)
            print(f"✅ Tarea creada: {task_data['title']}")
        else:
            task_data["_id"] = existing["_id"]
            print(f"ℹ️  Tarea ya existe: {task_data['title']}")
    
    # Crear comentarios de prueba
    comments_data = []
    comment_texts = [
        "Excelente progreso en esta tarea!",
        "@juan_dev ¿podrías revisar este código?",
        "He encontrado un bug en la implementación",
        "La documentación está actualizada",
        "@maria_pm necesitamos definir los requisitos",
        "Completado según especificaciones",
        "Requiere más pruebas antes del deploy",
        "@carlos_qa por favor revisar QA",
        "Optimización realizada con éxito",
        "Pendiente aprobación del cliente"
    ]
    
    # Crear comentarios para algunas tareas
    for i, task in enumerate(tasks_data[:10]):  # Solo para las primeras 10 tareas
        num_comments = random.randint(1, 3)
        for j in range(num_comments):
            comment = {
                "_id": ObjectId(),
                "content": random.choice(comment_texts),
                "task_id": task["_id"],
                "author_id": users_data[random.randint(1, 3)]["_id"],
                "created_at": task["created_at"] + timedelta(days=random.randint(1, 10)),
                "updated_at": task["created_at"] + timedelta(days=random.randint(1, 10)),
                "mentions": []
            }
            comments_data.append(comment)
    
    # Insertar comentarios
    for comment_data in comments_data:
        await db.comments.insert_one(comment_data)
    print(f"✅ {len(comments_data)} comentarios creados")
    
    # Crear registros de historial de ejemplo
    history_data = []
    actions = [
        "task_created", "task_updated", "task_completed",
        "task_assigned", "project_created", "comment_added"
    ]
    
    for i in range(50):  # 50 registros de historial
        history_record = {
            "_id": ObjectId(),
            "action": random.choice(actions),
            "description": f"Acción realizada en el sistema - {i+1}",
            "user_id": users_data[random.randint(0, 3)]["_id"],
            "entity_type": random.choice(["task", "project", "comment"]),
            "entity_id": ObjectId(),
            "timestamp": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            "changes": {}
        }
        history_data.append(history_record)
    
    # Insertar historial
    await db.history.insert_many(history_data)
    print(f"✅ {len(history_data)} registros de historial creados")
    
    # Crear notificaciones de ejemplo
    notifications_data = []
    notification_messages = [
        "Nueva tarea asignada: Revisar código",
        "Tarea completada en proyecto principal",
        "Comentario mencionándote en tarea",
        "Fecha límite próxima en 2 días",
        "Proyecto actualizado con nuevos requisitos"
    ]
    
    for i in range(20):
        notification = {
            "_id": ObjectId(),
            "user_id": users_data[random.randint(1, 3)]["_id"],
            "message": random.choice(notification_messages),
            "type": random.choice(["task_assigned", "task_completed", "comment_mention", "due_date_approaching"]),
            "read": random.choice([True, False]),
            "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 15)),
            "task_id": tasks_data[random.randint(0, len(tasks_data)-1)]["_id"] if random.choice([True, False]) else None,
            "priority": random.choice(["normal", "high"])
        }
        notifications_data.append(notification)
    
    # Insertar notificaciones
    await db.notifications.insert_many(notifications_data)
    print(f"✅ {len(notifications_data)} notificaciones creadas")
    
    # Mostrar estadísticas finales
    user_count = await db.users.count_documents({})
    project_count = await db.projects.count_documents({})
    task_count = await db.tasks.count_documents({})
    comment_count = await db.comments.count_documents({})
    notification_count = await db.notifications.count_documents({})
    
    print("\n📊 ESTADÍSTICAS FINALES:")
    print(f"👥 Usuarios: {user_count}")
    print(f"📁 Proyectos: {project_count}")
    print(f"✅ Tareas: {task_count}")
    print(f"💬 Comentarios: {comment_count}")
    print(f"🔔 Notificaciones: {notification_count}")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("📱 Credenciales de acceso:")
    print("   Admin: admin / admin123")
    print("   Usuario: juan_dev / password123")
    print("   Usuario: maria_pm / password123") 
    print("   Usuario: carlos_qa / password123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(populate_database())