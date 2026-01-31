"""
Router de Administración y Monitoreo del Sistema
Endpoints para administradores para monitorear rendimiento y estado
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from datetime import datetime
import psutil
import sys
from app.core.database import get_database
from app.models.user import UserInDB
from app.utils.dependencies import get_current_active_user
from app.utils.cache import get_cache_stats, invalidate_cache, cleanup_cache, QueryOptimizer
from app.middleware.logging_middleware import get_request_metrics, get_endpoint_stats, get_active_requests_count

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/system/status")
async def get_system_status(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estado general del sistema (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Información del sistema
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    disk = psutil.disk_usage('/')
    
    # Estadísticas de la base de datos
    db_stats = {}
    try:
        # Conteos de documentos
        db_stats = {
            "users": await db.users.count_documents({}),
            "projects": await db.projects.count_documents({}),
            "tasks": await db.tasks.count_documents({}),
            "comments": await db.comments.count_documents({}),
            "notifications": await db.notifications.count_documents({}),
            "history": await db.history.count_documents({})
        }
    except Exception as e:
        db_stats = {"error": str(e)}
    
    # Información de la aplicación
    app_info = {
        "python_version": sys.version,
        "uptime": "N/A",  # Se podría implementar con timestamp de inicio
        "environment": "development"  # Se podría obtener de configuración
    }
    
    return {
        "timestamp": datetime.utcnow(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "database": db_stats,
        "application": app_info,
        "cache": get_cache_stats()
    }

@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener estadísticas del sistema de caché (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return get_cache_stats()

@router.post("/cache/clear")
async def clear_cache(
    pattern: str = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Limpiar caché completo o por patrón (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    cleared_count = invalidate_cache(pattern)
    
    return {
        "message": f"Cache cleared successfully",
        "pattern": pattern or "all",
        "entries_cleared": cleared_count,
        "timestamp": datetime.utcnow()
    }

@router.post("/cache/cleanup")
async def manual_cache_cleanup(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Ejecutar limpieza manual del caché (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    cleaned_count = cleanup_cache()
    
    return {
        "message": "Cache cleanup completed",
        "entries_cleaned": cleaned_count,
        "timestamp": datetime.utcnow()
    }

@router.get("/database/indexes")
async def get_database_indexes_script(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener script para crear índices optimizados (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return {
        "script": QueryOptimizer.create_indexes_script(),
        "description": "MongoDB index creation script for optimal performance",
        "timestamp": datetime.utcnow()
    }

@router.get("/database/collections/stats")
async def get_collections_stats(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Obtener estadísticas detalladas de las colecciones (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    collections = ["users", "projects", "tasks", "comments", "notifications", "history"]
    stats = {}
    
    for collection_name in collections:
        try:
            collection = getattr(db, collection_name)
            
            # Estadísticas básicas
            count = await collection.count_documents({})
            
            # Obtener algunos documentos para analizar estructura
            sample_docs = await collection.find({}).limit(5).to_list(length=5)
            
            # Calcular tamaño promedio (aproximado)
            avg_size = 0
            if sample_docs:
                total_size = sum(len(str(doc)) for doc in sample_docs)
                avg_size = total_size / len(sample_docs)
            
            stats[collection_name] = {
                "document_count": count,
                "estimated_avg_size": avg_size,
                "estimated_total_size": count * avg_size,
                "sample_structure": list(sample_docs[0].keys()) if sample_docs else []
            }
            
        except Exception as e:
            stats[collection_name] = {"error": str(e)}
    
    return {
        "timestamp": datetime.utcnow(),
        "collections": stats
    }

@router.get("/performance/slow-queries")
async def get_slow_queries_analysis(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Análisis de consultas lentas y recomendaciones (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Simulación de análisis de consultas lentas
    # En un entorno real, esto se obtendría de logs de MongoDB
    slow_queries = [
        {
            "query": "db.tasks.find({assigned_to: ObjectId}).sort({created_at: -1})",
            "duration_ms": 1200,
            "collection": "tasks",
            "recommendation": "Create compound index on {assigned_to: 1, created_at: -1}",
            "severity": "high"
        },
        {
            "query": "db.notifications.find({user_id: ObjectId, read: false})",
            "duration_ms": 800,
            "collection": "notifications",
            "recommendation": "Create compound index on {user_id: 1, read: 1}",
            "severity": "medium"
        }
    ]
    
    return {
        "timestamp": datetime.utcnow(),
        "slow_queries": slow_queries,
        "recommendations": [
            "Enable MongoDB profiler to collect real slow query data",
            "Consider implementing query result caching for frequent operations",
            "Review and optimize aggregation pipelines",
            "Monitor index usage and remove unused indexes"
        ]
    }

@router.get("/users/activity-summary")
async def get_users_activity_summary(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Resumen de actividad de usuarios (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Obtener estadísticas de actividad de usuarios
    pipeline = [
        {
            "$lookup": {
                "from": "tasks",
                "localField": "_id",
                "foreignField": "assigned_to",
                "as": "assigned_tasks"
            }
        },
        {
            "$lookup": {
                "from": "comments",
                "localField": "_id",
                "foreignField": "author_id", 
                "as": "comments"
            }
        },
        {
            "$addFields": {
                "total_assigned_tasks": {"$size": "$assigned_tasks"},
                "completed_tasks": {
                    "$size": {
                        "$filter": {
                            "input": "$assigned_tasks",
                            "cond": {"$eq": ["$$this.status", "Completada"]}
                        }
                    }
                },
                "total_comments": {"$size": "$comments"}
            }
        },
        {
            "$project": {
                "username": 1,
                "email": 1,
                "is_active": 1,
                "created_at": 1,
                "total_assigned_tasks": 1,
                "completed_tasks": 1,
                "total_comments": 1,
                "completion_rate": {
                    "$cond": [
                        {"$eq": ["$total_assigned_tasks", 0]},
                        0,
                        {"$multiply": [{"$divide": ["$completed_tasks", "$total_assigned_tasks"]}, 100]}
                    ]
                }
            }
        },
        {"$sort": {"total_assigned_tasks": -1}}
    ]
    
    users_activity = await db.users.aggregate(pipeline).to_list(length=None)
    
    # Estadísticas generales
    total_users = len(users_activity)
    active_users = sum(1 for user in users_activity if user.get("is_active", False))
    users_with_tasks = sum(1 for user in users_activity if user.get("total_assigned_tasks", 0) > 0)
    
    return {
        "timestamp": datetime.utcnow(),
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "users_with_tasks": users_with_tasks,
            "average_tasks_per_user": sum(user.get("total_assigned_tasks", 0) for user in users_activity) / total_users if total_users > 0 else 0
        },
        "users": users_activity
    }

@router.get("/health")
async def health_check():
    """Health check endpoint para monitoreo externo"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "service": "Task Manager API"
    }

@router.get("/metrics")
async def get_system_metrics(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Métricas del sistema en formato compatible con Prometheus (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Obtener métricas básicas
    metrics = {
        "http_requests_total": "N/A",  # Se implementaría con middleware
        "http_request_duration_seconds": "N/A",
        "database_connections": "N/A",
        "cache_hits_total": "N/A",
        "cache_misses_total": "N/A"
    }
    
    # Métricas de negocio
    business_metrics = {
        "tasks_total": await db.tasks.count_documents({}),
        "tasks_completed": await db.tasks.count_documents({"status": "Completada"}),
        "tasks_pending": await db.tasks.count_documents({"status": "Pendiente"}),
        "users_active": await db.users.count_documents({"is_active": True}),
        "projects_active": await db.projects.count_documents({"status": "active"})
    }
    
    return {
        "timestamp": datetime.utcnow(),
        "system_metrics": metrics,
        "business_metrics": business_metrics,
        "cache_metrics": get_cache_stats()
    }

@router.post("/maintenance/cleanup")
async def run_maintenance_cleanup(
    current_user: UserInDB = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """Ejecutar tareas de mantenimiento del sistema (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    cleanup_results = {}
    
    try:
        # Limpiar notificaciones expiradas
        expired_notifications = await db.notifications.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        cleanup_results["expired_notifications"] = expired_notifications.deleted_count
        
        # Limpiar notificaciones leídas muy antiguas (más de 90 días)
        from datetime import timedelta
        old_read_notifications = await db.notifications.delete_many({
            "read": True,
            "created_at": {"$lt": datetime.utcnow() - timedelta(days=90)}
        })
        cleanup_results["old_read_notifications"] = old_read_notifications.deleted_count
        
        # Limpiar historial muy antiguo (más de 1 año)
        old_history = await db.history.delete_many({
            "timestamp": {"$lt": datetime.utcnow() - timedelta(days=365)}
        })
        cleanup_results["old_history"] = old_history.deleted_count
        
        # Limpiar caché
        cache_cleaned = cleanup_cache()
        cleanup_results["cache_entries_cleaned"] = cache_cleaned
        
        cleanup_results["status"] = "success"
        cleanup_results["total_cleaned"] = sum([
            expired_notifications.deleted_count,
            old_read_notifications.deleted_count,
            old_history.deleted_count,
            cache_cleaned
        ])
        
    except Exception as e:
        cleanup_results["status"] = "error"
        cleanup_results["error"] = str(e)
    
    cleanup_results["timestamp"] = datetime.utcnow()
    return cleanup_results

@router.get("/metrics/requests")
async def get_request_metrics_endpoint(
    minutes: int = 5,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener métricas de requests de los últimos N minutos (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return get_request_metrics(minutes)

@router.get("/metrics/endpoints")
async def get_endpoint_metrics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener estadísticas detalladas por endpoint (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return get_endpoint_stats()

@router.get("/metrics/realtime")
async def get_realtime_metrics(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Obtener métricas en tiempo real (solo admin)"""
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return {
        "active_requests": get_active_requests_count(),
        "timestamp": datetime.utcnow(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    }