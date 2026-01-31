"""
Configuración de Production y Optimizaciones
Configuraciones específicas para entorno de producción
"""
from pydantic_settings import BaseSettings
from typing import List

class ProductionSettings(BaseSettings):
    """Configuración específica para producción"""
    
    # Base de datos
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "task_manager_prod"
    
    # Pool de conexiones de MongoDB
    mongodb_max_connections: int = 100
    mongodb_min_connections: int = 10
    mongodb_max_idle_time_ms: int = 30000
    mongodb_server_selection_timeout_ms: int = 5000
    
    # Seguridad
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION"
    access_token_expire_minutes: int = 30  # Más corto en producción
    
    # Caché
    enable_caching: bool = True
    cache_default_ttl: int = 300
    cache_max_size: int = 5000
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS más restrictivo
    allowed_origins: str = "https://yourdomain.com"
    
    # Performance
    enable_compression: bool = True
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    
    # Monitoring
    enable_metrics: bool = True
    metrics_endpoint: str = "/metrics"
    
    class Config:
        env_prefix = "PROD_"
        env_file = ".env.production"

# Configuraciones de índices de MongoDB para producción
MONGODB_INDEXES = {
    "users": [
        {"keys": [("username", 1)], "unique": True},
        {"keys": [("email", 1)], "unique": True},
        {"keys": [("is_active", 1), ("created_at", -1)]},
    ],
    "projects": [
        {"keys": [("created_by", 1), ("status", 1)]},
        {"keys": [("status", 1), ("end_date", 1)]},
        {"keys": [("name", "text"), ("description", "text")]},
    ],
    "tasks": [
        {"keys": [("status", 1), ("due_date", 1)]},
        {"keys": [("assigned_to", 1), ("status", 1), ("created_at", -1)]},
        {"keys": [("project_id", 1), ("status", 1)]},
        {"keys": [("created_at", -1)]},
        {"keys": [("updated_at", -1)]},
        {"keys": [("title", "text"), ("description", "text")]},
        # Índice compuesto para consultas frecuentes
        {"keys": [("assigned_to", 1), ("status", 1), ("due_date", 1)]},
    ],
    "comments": [
        {"keys": [("task_id", 1), ("created_at", -1)]},
        {"keys": [("author_id", 1), ("created_at", -1)]},
        {"keys": [("mentions", 1)]},
    ],
    "notifications": [
        {"keys": [("user_id", 1), ("read", 1), ("created_at", -1)]},
        {"keys": [("expires_at", 1)]},
        {"keys": [("type", 1), ("created_at", -1)]},
    ],
    "history": [
        {"keys": [("user_id", 1), ("timestamp", -1)]},
        {"keys": [("entity_type", 1), ("entity_id", 1), ("timestamp", -1)]},
        {"keys": [("action", 1), ("timestamp", -1)]},
    ]
}

# Configuraciones de agregación optimizadas
OPTIMIZED_AGGREGATIONS = {
    "task_statistics": [
        {"$match": {"created_at": {"$gte": "START_DATE"}}},  # Filtrar primero
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "avg_estimated_hours": {"$avg": "$estimated_hours"}
        }},
        {"$sort": {"count": -1}}
    ],
    "user_productivity": [
        {"$match": {"assigned_to": {"$ne": None}}},
        {"$group": {
            "_id": "$assigned_to",
            "total_tasks": {"$sum": 1},
            "completed_tasks": {"$sum": {"$cond": [{"$eq": ["$status", "Completada"]}, 1, 0]}},
            "avg_completion_time": {"$avg": "$actual_hours"}
        }},
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$sort": {"completed_tasks": -1}}
    ]
}

# Configuraciones de logging para producción
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 3
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "app": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Configuraciones de seguridad
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Rate limiting configurations
RATE_LIMIT_RULES = {
    "/api/v1/auth/login": {"requests": 5, "window": 60},  # 5 intentos por minuto
    "/api/v1/auth/register": {"requests": 3, "window": 60},  # 3 registros por minuto
    "/api/v1/dashboard/*": {"requests": 30, "window": 60},  # 30 requests por minuto
    "/api/v1/tasks": {"requests": 100, "window": 60},  # 100 requests por minuto
    "default": {"requests": 60, "window": 60}  # 60 requests por minuto por defecto
}

# Configuraciones de monitoreo y métricas
MONITORING_CONFIG = {
    "enable_prometheus": True,
    "metrics_port": 9090,
    "health_check_interval": 30,  # segundos
    "collect_business_metrics": True,
    "alert_thresholds": {
        "response_time_95th_percentile": 2.0,  # segundos
        "error_rate": 0.05,  # 5%
        "memory_usage": 0.85,  # 85%
        "cpu_usage": 0.80,  # 80%
        "disk_usage": 0.90,  # 90%
    }
}

# Configuraciones de backup y mantenimiento
MAINTENANCE_CONFIG = {
    "backup_enabled": True,
    "backup_schedule": "0 2 * * *",  # Diario a las 2:00 AM
    "backup_retention_days": 30,
    "cleanup_schedule": "0 3 * * 0",  # Domingos a las 3:00 AM
    "cleanup_rules": {
        "notifications_retention_days": 90,
        "history_retention_days": 365,
        "logs_retention_days": 30
    }
}

# Configuraciones de cache para diferentes tipos de datos
CACHE_STRATEGIES = {
    "dashboard": {
        "ttl": 120,  # 2 minutos
        "strategy": "write-through"
    },
    "statistics": {
        "ttl": 300,  # 5 minutos
        "strategy": "cache-aside"
    },
    "user_profile": {
        "ttl": 600,  # 10 minutos
        "strategy": "write-through"
    },
    "tasks_list": {
        "ttl": 60,  # 1 minuto
        "strategy": "cache-aside"
    }
}