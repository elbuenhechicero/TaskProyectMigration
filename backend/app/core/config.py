"""
Configuración de la aplicación FastAPI
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""
    
    # API Settings
    api_prefix: str = "/api/v1"
    debug: bool = True
    project_name: str = "Task Manager API"
    version: str = "1.0.0"
    
    # Database
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "task_manager"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    @property
    def origins_list(self) -> List[str]:
        """Convertir string de origins a lista"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Crear instancia global de settings
settings = Settings()