"""
Script de configuración para entorno de producción
Configura índices, logging y optimizaciones
"""
import asyncio
import logging
import logging.config
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.config.production import (
    MONGODB_INDEXES, LOGGING_CONFIG, SECURITY_HEADERS,
    ProductionSettings
)

# Configurar logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

async def create_mongodb_indexes():
    """Crear índices optimizados en MongoDB"""
    settings = Settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    
    logger.info("Iniciando creación de índices MongoDB...")
    
    for collection_name, indexes in MONGODB_INDEXES.items():
        collection = getattr(db, collection_name)
        
        for index_config in indexes:
            try:
                keys = index_config["keys"]
                options = {k: v for k, v in index_config.items() if k != "keys"}
                
                await collection.create_index(keys, **options)
                logger.info(f"Índice creado en {collection_name}: {keys}")
                
            except Exception as e:
                logger.error(f"Error creando índice en {collection_name}: {e}")
    
    # Verificar índices existentes
    for collection_name in MONGODB_INDEXES.keys():
        collection = getattr(db, collection_name)
        indexes_info = await collection.list_indexes().to_list(length=None)
        
        logger.info(f"Índices en {collection_name}:")
        for index in indexes_info:
            logger.info(f"  - {index['name']}: {index.get('key', {})}")
    
    client.close()
    logger.info("Configuración de índices completada")

async def run_database_optimization():
    """Ejecutar optimizaciones de base de datos"""
    settings = Settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    
    logger.info("Ejecutando optimizaciones de base de datos...")
    
    try:
        # Obtener estadísticas de las colecciones
        collections = await db.list_collection_names()
        
        for collection_name in collections:
            collection = db[collection_name]
            stats = await db.command("collStats", collection_name)
            
            logger.info(f"Estadísticas de {collection_name}:")
            logger.info(f"  - Documentos: {stats.get('count', 0):,}")
            logger.info(f"  - Tamaño promedio: {stats.get('avgObjSize', 0):,.0f} bytes")
            logger.info(f"  - Tamaño total: {stats.get('size', 0):,.0f} bytes")
            logger.info(f"  - Índices: {stats.get('nindexes', 0)}")
        
        # Ejecutar comando de compactación si es necesario
        logger.info("Optimizaciones completadas")
        
    except Exception as e:
        logger.error(f"Error en optimizaciones: {e}")
    finally:
        client.close()

def setup_production_logging():
    """Configurar logging para producción"""
    import os
    
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Aplicar configuración de logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    logger = logging.getLogger("app")
    logger.info("Sistema de logging configurado para producción")
    
    return logger

def generate_nginx_config():
    """Generar configuración de Nginx para producción"""
    nginx_config = """
# Configuración de Nginx para Task Manager API
server {
    listen 80;
    server_name your-domain.com;
    
    # Redireccionar HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # Configuración SSL
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # API Routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Auth endpoints with stricter rate limiting
    location /api/v1/auth/ {
        limit_req zone=login burst=5 nodelay;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/api/v1/admin/health;
    }
    
    # Block access to sensitive files
    location ~ /\\.env {
        deny all;
        return 404;
    }
    
    location ~ /logs/ {
        deny all;
        return 404;
    }
}
"""
    
    with open("nginx.conf", "w") as f:
        f.write(nginx_config)
    
    logger.info("Configuración de Nginx generada: nginx.conf")

def generate_docker_config():
    """Generar configuración de Docker para producción"""
    dockerfile = """
# Dockerfile para Task Manager API - Producción
FROM python:3.11-slim

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROD_DEBUG=false

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio de logs
RUN mkdir -p logs && chown -R app:app logs

# Cambiar a usuario no-root
USER app

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/v1/admin/health || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
    
    docker_compose = """
version: '3.8'

services:
  api:
    build: .
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PROD_MONGODB_URI=mongodb://mongo:27017
      - PROD_DATABASE_NAME=task_manager_prod
      - PROD_SECRET_KEY=your-super-secret-key-change-this
    depends_on:
      - mongo
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - taskmanager
    
  mongo:
    image: mongo:6.0
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init:/docker-entrypoint-initdb.d
    networks:
      - taskmanager
  
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - taskmanager
  
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    networks:
      - taskmanager

volumes:
  mongodb_data:
  redis_data:

networks:
  taskmanager:
    driver: bridge
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    with open("docker-compose.prod.yml", "w") as f:
        f.write(docker_compose)
    
    logger.info("Configuración de Docker generada")

def generate_systemd_service():
    """Generar archivo de servicio systemd"""
    service_config = """
[Unit]
Description=Task Manager API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/taskmanager
Environment=PATH=/opt/taskmanager/venv/bin
ExecStart=/opt/taskmanager/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
TimeoutStopSec=30

# Security settings
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/taskmanager/logs
PrivateTmp=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes

[Install]
WantedBy=multi-user.target
"""
    
    with open("taskmanager.service", "w") as f:
        f.write(service_config)
    
    logger.info("Archivo de servicio systemd generado: taskmanager.service")

async def main():
    """Función principal de configuración"""
    logger = setup_production_logging()
    logger.info("Iniciando configuración de producción...")
    
    # Crear índices de MongoDB
    await create_mongodb_indexes()
    
    # Ejecutar optimizaciones
    await run_database_optimization()
    
    # Generar archivos de configuración
    generate_nginx_config()
    generate_docker_config()
    generate_systemd_service()
    
    logger.info("Configuración de producción completada")
    logger.info("Archivos generados:")
    logger.info("  - nginx.conf")
    logger.info("  - Dockerfile")
    logger.info("  - docker-compose.prod.yml")
    logger.info("  - taskmanager.service")

if __name__ == "__main__":
    asyncio.run(main())