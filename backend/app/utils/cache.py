"""
Sistema de caché en memoria y optimizaciones de rendimiento
"""
from fastapi import Request, Response
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import hashlib
import asyncio
from functools import wraps
import logging

# Cache en memoria simple
memory_cache: Dict[str, Dict[str, Any]] = {}

class CacheConfig:
    """Configuración del sistema de caché"""
    DEFAULT_TTL = 300  # 5 minutos
    MAX_CACHE_SIZE = 1000  # Máximo número de entradas
    
    # TTLs específicos por tipo de dato
    TTL_STATS = 180      # 3 minutos para estadísticas
    TTL_DASHBOARD = 120  # 2 minutos para dashboard
    TTL_REPORTS = 600    # 10 minutos para reportes
    TTL_TASKS = 60       # 1 minuto para listas de tareas
    TTL_USERS = 300      # 5 minutos para usuarios

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generar clave de caché única"""
    # Crear string con todos los argumentos
    key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    # Agregar kwargs ordenados
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted_kwargs)
        key_data += f":{kwargs_str}"
    
    # Hash para mantener claves cortas
    return hashlib.md5(key_data.encode()).hexdigest()

def is_cache_expired(timestamp: datetime, ttl: int) -> bool:
    """Verificar si una entrada de caché ha expirado"""
    return datetime.utcnow() > timestamp + timedelta(seconds=ttl)

def get_cache(key: str) -> Optional[Any]:
    """Obtener valor del caché"""
    if key in memory_cache:
        entry = memory_cache[key]
        
        # Verificar si ha expirado
        if is_cache_expired(entry["timestamp"], entry["ttl"]):
            del memory_cache[key]
            return None
        
        # Actualizar último acceso
        memory_cache[key]["last_accessed"] = datetime.utcnow()
        return entry["data"]
    
    return None

def set_cache(key: str, data: Any, ttl: int = CacheConfig.DEFAULT_TTL) -> None:
    """Guardar valor en el caché"""
    # Limpiar caché si está lleno
    if len(memory_cache) >= CacheConfig.MAX_CACHE_SIZE:
        cleanup_cache()
    
    memory_cache[key] = {
        "data": data,
        "timestamp": datetime.utcnow(),
        "last_accessed": datetime.utcnow(),
        "ttl": ttl
    }

def invalidate_cache(pattern: str = None) -> int:
    """Invalidar entradas del caché por patrón"""
    if pattern is None:
        # Limpiar todo el caché
        count = len(memory_cache)
        memory_cache.clear()
        return count
    
    # Limpiar entradas que coincidan con el patrón
    keys_to_delete = [key for key in memory_cache.keys() if pattern in key]
    for key in keys_to_delete:
        del memory_cache[key]
    
    return len(keys_to_delete)

def cleanup_cache() -> int:
    """Limpiar entradas expiradas y menos usadas"""
    current_time = datetime.utcnow()
    keys_to_delete = []
    
    # Eliminar entradas expiradas
    for key, entry in memory_cache.items():
        if is_cache_expired(entry["timestamp"], entry["ttl"]):
            keys_to_delete.append(key)
    
    # Si todavía hay demasiadas entradas, eliminar las menos accedidas
    if len(memory_cache) - len(keys_to_delete) > CacheConfig.MAX_CACHE_SIZE * 0.8:
        # Ordenar por último acceso y eliminar las más antiguas
        sorted_entries = sorted(
            memory_cache.items(),
            key=lambda x: x[1]["last_accessed"]
        )
        
        # Eliminar el 20% más antiguo
        cleanup_count = int(len(sorted_entries) * 0.2)
        for key, _ in sorted_entries[:cleanup_count]:
            keys_to_delete.append(key)
    
    # Ejecutar limpieza
    for key in keys_to_delete:
        if key in memory_cache:
            del memory_cache[key]
    
    return len(keys_to_delete)

def cache_response(ttl: int = CacheConfig.DEFAULT_TTL, prefix: str = "api"):
    """Decorador para cachear respuestas de endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = generate_cache_key(prefix, func.__name__, *args[1:], **kwargs)
            
            # Intentar obtener del caché
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def get_cache_stats() -> Dict[str, Any]:
    """Obtener estadísticas del caché"""
    current_time = datetime.utcnow()
    expired_count = 0
    total_size = 0
    
    for entry in memory_cache.values():
        if is_cache_expired(entry["timestamp"], entry["ttl"]):
            expired_count += 1
        
        # Estimar tamaño (aproximado)
        total_size += len(str(entry["data"]))
    
    return {
        "total_entries": len(memory_cache),
        "expired_entries": expired_count,
        "active_entries": len(memory_cache) - expired_count,
        "estimated_size_bytes": total_size,
        "max_size": CacheConfig.MAX_CACHE_SIZE,
        "hit_rate": None,  # Se podría implementar con contadores
        "cache_utilization": len(memory_cache) / CacheConfig.MAX_CACHE_SIZE * 100
    }

class CacheInvalidationService:
    """Servicio para invalidar caché cuando los datos cambian"""
    
    @staticmethod
    def invalidate_task_caches(task_id: str = None, project_id: str = None):
        """Invalidar cachés relacionados con tareas"""
        patterns = ["dashboard", "stats", "tasks", "reports"]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += invalidate_cache(pattern)
        
        logging.info(f"Invalidated {total_invalidated} cache entries for task changes")
        return total_invalidated
    
    @staticmethod
    def invalidate_project_caches(project_id: str = None):
        """Invalidar cachés relacionados con proyectos"""
        patterns = ["dashboard", "stats", "projects", "reports"]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += invalidate_cache(pattern)
        
        logging.info(f"Invalidated {total_invalidated} cache entries for project changes")
        return total_invalidated
    
    @staticmethod
    def invalidate_user_caches(user_id: str = None):
        """Invalidar cachés relacionados con usuarios"""
        patterns = ["dashboard", "stats", "users", "productivity"]
        
        total_invalidated = 0
        for pattern in patterns:
            total_invalidated += invalidate_cache(pattern)
        
        logging.info(f"Invalidated {total_invalidated} cache entries for user changes")
        return total_invalidated

# Middleware de caché HTTP
class CacheMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Solo cachear GET requests
            if request.method == "GET":
                # Generar clave de caché basada en la URL y query params
                cache_key = generate_cache_key(
                    "http",
                    str(request.url),
                    request.headers.get("authorization", "")[:20]  # Incluir usuario
                )
                
                # Verificar caché
                cached_response = get_cache(cache_key)
                if cached_response is not None:
                    response = Response(
                        content=cached_response["body"],
                        status_code=cached_response["status_code"],
                        headers=cached_response["headers"]
                    )
                    await response(scope, receive, send)
                    return
            
            # Continuar con la aplicación normal
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

# Utilidades de optimización de consultas
class QueryOptimizer:
    """Utilidades para optimizar consultas a la base de datos"""
    
    @staticmethod
    def create_indexes_script() -> str:
        """Generar script para crear índices óptimos"""
        indexes = [
            # Índices para tareas
            'db.tasks.createIndex({"status": 1, "due_date": 1})',
            'db.tasks.createIndex({"assigned_to": 1, "status": 1})',
            'db.tasks.createIndex({"project_id": 1, "status": 1})',
            'db.tasks.createIndex({"created_at": -1})',
            'db.tasks.createIndex({"updated_at": -1})',
            
            # Índices para proyectos
            'db.projects.createIndex({"created_by": 1, "status": 1})',
            'db.projects.createIndex({"status": 1, "end_date": 1})',
            
            # Índices para comentarios
            'db.comments.createIndex({"task_id": 1, "created_at": -1})',
            'db.comments.createIndex({"author_id": 1, "created_at": -1})',
            
            # Índices para notificaciones
            'db.notifications.createIndex({"user_id": 1, "read": 1})',
            'db.notifications.createIndex({"user_id": 1, "created_at": -1})',
            'db.notifications.createIndex({"expires_at": 1})',
            
            # Índices para historial
            'db.history.createIndex({"user_id": 1, "timestamp": -1})',
            'db.history.createIndex({"entity_type": 1, "entity_id": 1, "timestamp": -1})',
            
            # Índices para usuarios
            'db.users.createIndex({"username": 1}, {unique: true})',
            'db.users.createIndex({"email": 1}, {unique: true})',
            'db.users.createIndex({"is_active": 1})'
        ]
        
        return "// MongoDB Index Creation Script\n" + "\n".join(indexes)
    
    @staticmethod
    def get_aggregation_pipeline_stats(pipeline: list) -> dict:
        """Analizar pipeline de agregación para optimizaciones"""
        stats = {
            "stages": len(pipeline),
            "has_match_first": False,
            "has_sort": False,
            "has_limit": False,
            "potential_optimizations": []
        }
        
        if pipeline and "$match" in str(pipeline[0]):
            stats["has_match_first"] = True
        else:
            stats["potential_optimizations"].append("Move $match to beginning")
        
        for stage in pipeline:
            if "$sort" in stage:
                stats["has_sort"] = True
            if "$limit" in stage:
                stats["has_limit"] = True
        
        if stats["has_sort"] and not stats["has_limit"]:
            stats["potential_optimizations"].append("Add $limit after $sort")
        
        return stats

# Background tasks para limpieza de caché
async def cache_cleanup_task():
    """Tarea background para limpiar caché periódicamente"""
    while True:
        try:
            cleaned = cleanup_cache()
            if cleaned > 0:
                logging.info(f"Cache cleanup: removed {cleaned} entries")
            
            # Esperar 5 minutos antes de la próxima limpieza
            await asyncio.sleep(300)
        except Exception as e:
            logging.error(f"Error in cache cleanup task: {e}")
            await asyncio.sleep(60)  # Esperar un minuto en caso de error