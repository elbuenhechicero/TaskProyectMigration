# Task Manager - Frontend + Backend

Sistema de gestión de tareas con API en Flask (Python), MongoDB y frontend con arquitectura MVC y Tailwind CSS.

## Estructura

- **backend/** – API REST con Flask, JWT y MongoDB
- **frontend/** – SPA con MVC, Tailwind y consumo de la API
- **legacyapp-main/** – Aplicación legacy original (solo referencia)

## Backend (Flask + MongoDB)

### Configuración

1. Crea un archivo `.env` en la carpeta `backend/` (puedes copiar `.env.example`).
2. Define tu URI de MongoDB:

```env
MONGO_URI=tu_uri_de_mongodb_aqui
MONGO_DB_NAME=taskmanager
SECRET_KEY=una-clave-secreta-segura
```

### Instalación y ejecución

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
python app.py
```

La API quedará en `http://localhost:5000`.

### Endpoints principales

- `POST /api/auth/login` – Login (devuelve JWT)
- `GET /api/auth/me` – Usuario actual
- `GET /api/auth/users` – Lista de usuarios
- `GET/POST /api/tasks` – Listar / crear tareas
- `GET/PUT/DELETE /api/tasks/<id>` – Obtener / actualizar / eliminar tarea
- `POST /api/tasks/search` – Búsqueda con filtros
- `GET /api/tasks/stats` – Estadísticas
- `GET/POST /api/projects` – Proyectos
- `GET/POST /api/comments?taskId=` – Comentarios
- `GET /api/history?taskId=` – Historial
- `GET /api/notifications` – Notificaciones
- `POST /api/notifications/read` – Marcar leídas
- `GET /api/reports/<tasks|projects|users>` – Reportes
- `GET /api/reports/export/csv` – Exportar CSV

## Frontend

Abre `frontend/index.html` en el navegador. **Recomendado:** sirve la carpeta con un servidor local (p. ej. `npx serve frontend -l 3000`) para que las vistas se carguen por `fetch` sin problemas de CORS con `file://`.

- **index.html** – Shell: cabecera, navegación y contenedores vacíos.
- **views/** – Una vista por archivo HTML (login, tasks, projects, comments, history, notifications, search, reports). El servicio `ViewLoader` las carga al iniciar y las inyecta en el DOM.
- **js/views/** – Lógica de presentación (JS). **js/controllers/** – Controladores. **js/services/** – API y `ViewLoader`.

Para desarrollo con la API en otro puerto, edita `frontend/js/config.js` y cambia `API_BASE_URL` si es necesario.

### Uso por defecto

- Usuario: `admin`
- Contraseña: `admin`

## Mejoras aplicadas respecto al legacy

- **Seguridad:** Contraseñas con hash (Werkzeug), JWT para sesión, sanitización en frontend para evitar XSS
- **Arquitectura:** Backend API + frontend MVC (modelos/vistas/controladores y servicios)
- **Base de datos:** MongoDB con espacio para tu URI en `.env`
- **UX:** Toasts en lugar de `alert`, fila seleccionada resaltada, input tipo fecha, validaciones
- **Código:** Módulos separados, eventos con `addEventListener`, sin `event` global en pestañas
