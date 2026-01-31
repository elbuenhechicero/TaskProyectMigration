"""
Conexión a la base de datos MongoDB usando Motor (driver async)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    """Clase para manejar la conexión a MongoDB"""
    
    def __init__(self):
        self.client = None  # AsyncIOMotorClient
        self.database = None
        
    async def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.database = self.client[settings.database_name]
            
            # Verificar conexión
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {settings.database_name}")
            
            # Crear índices necesarios
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Desconectar de MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Crear índices necesarios para optimizar consultas"""
        try:
            # Índices para usuarios
            await self.database.users.create_index("username", unique=True)
            await self.database.users.create_index("email", unique=True)
            
            # Índices para tareas
            await self.database.tasks.create_index("title")
            await self.database.tasks.create_index("status")
            await self.database.tasks.create_index("priority")
            await self.database.tasks.create_index("assignedTo")
            await self.database.tasks.create_index("projectId")
            await self.database.tasks.create_index("dueDate")
            await self.database.tasks.create_index("createdAt")
            
            # Índices para proyectos
            await self.database.projects.create_index("name", unique=True)
            
            # Índices para comentarios
            await self.database.comments.create_index("taskId")
            await self.database.comments.create_index("createdAt")
            
            # Índices para historial
            await self.database.history.create_index("taskId")
            await self.database.history.create_index("userId")
            await self.database.history.create_index("timestamp")
            
            # Índices para notificaciones
            await self.database.notifications.create_index("userId")
            await self.database.notifications.create_index("read")
            await self.database.notifications.create_index("createdAt")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

# Instancia global de la base de datos
mongodb = MongoDB()

async def get_database():
    """Obtener la instancia de la base de datos"""
    return mongodb.database