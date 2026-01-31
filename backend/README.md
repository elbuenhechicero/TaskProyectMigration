# FastAPI Task Manager Backend

Esta es la API backend del sistema de gestión de tareas, desarrollada con FastAPI y MongoDB.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/          # Configuración y settings
│   ├── models/        # Modelos Pydantic y MongoDB
│   ├── routers/       # Rutas de la API
│   ├── services/      # Lógica de negocio
│   └── utils/         # Utilidades y helpers
├── main.py           # Punto de entrada de la aplicación
├── requirements.txt  # Dependencias de Python
└── .env.example     # Variables de entorno de ejemplo
```

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Ejecutar la aplicación:
```bash
python main.py
```

## Documentación

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment en Render.com

La aplicación está configurada para desplegarse fácilmente en Render.com.

## API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Login de usuario
- `POST /api/v1/auth/register` - Registro de usuario

### Tareas
- `GET /api/v1/tasks` - Listar tareas
- `POST /api/v1/tasks` - Crear tarea
- `GET /api/v1/tasks/{id}` - Obtener tarea
- `PUT /api/v1/tasks/{id}` - Actualizar tarea
- `DELETE /api/v1/tasks/{id}` - Eliminar tarea

### Proyectos
- `GET /api/v1/projects` - Listar proyectos
- `POST /api/v1/projects` - Crear proyecto
- `PUT /api/v1/projects/{id}` - Actualizar proyecto
- `DELETE /api/v1/projects/{id}` - Eliminar proyecto

(Más endpoints en desarrollo...)