# Task Manager Frontend

Frontend estático para la aplicación Task Manager desarrollado con HTML, CSS y JavaScript vanilla.

## 🚀 Despliegue en Producción

### Prerrequisitos
- Tu código debe estar en un repositorio Git (GitHub, GitLab, etc.)
- El backend debe estar desplegado y funcionando

### Desplegar en Vercel

#### Opción 1: Usando Vercel CLI
1. Instala Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. En la carpeta frontend, ejecuta:
   ```bash
   vercel
   ```

3. Sigue las instrucciones en pantalla

#### Opción 2: Usando GitHub (Recomendado)
1. Ve a [vercel.com](https://vercel.com)
2. Haz clic en "New Project"
3. Conecta tu repositorio de GitHub
4. Selecciona la carpeta `frontend` como el directorio raíz
5. Vercel detectará automáticamente que es un sitio estático
6. Haz clic en "Deploy"

### Desplegar en Render

#### Opción 1: Usando render.yaml
1. Ve a [render.com](https://render.com)
2. Haz clic en "New" -> "Blueprint"
3. Conecta tu repositorio
4. Render detectará el archivo `render.yaml` en la carpeta frontend
5. Haz clic en "Apply"

#### Opción 2: Sitio Web Estático
1. Ve a [render.com](https://render.com)
2. Haz clic en "New" -> "Static Site"
3. Conecta tu repositorio
4. Configura:
   - **Root Directory**: `frontend`
   - **Build Command**: `echo "Build completed"`
   - **Publish Directory**: `.`
5. Haz clic en "Create Static Site"

## 🔧 Configuración

### Variables de Entorno
La URL del API está configurada en `js/config.js`. Asegúrate de que apunte a tu backend en producción:

```javascript
const Config = {
  API_BASE_URL: "https://taskproyectmigration.onrender.com/api",
};
```

### Archivos de Configuración
- `package.json`: Metadatos del proyecto
- `vercel.json`: Configuración específica para Vercel
- `render.yaml`: Configuración específica para Render

## 📁 Estructura del Proyecto
```
frontend/
├── index.html          # Página principal
├── css/
│   └── main.css        # Estilos principales
├── js/
│   ├── app.js         # Aplicación principal
│   ├── config.js      # Configuración
│   ├── controllers/   # Controladores
│   ├── services/      # Servicios
│   ├── utils/         # Utilidades
│   └── views/         # Vistas JavaScript
├── views/             # Templates HTML
└── files de configuración
```

## 🌐 URLs de Producción
- **Vercel**: Se generará automáticamente (ej: `https://tu-app.vercel.app`)
- **Render**: Se generará automáticamente (ej: `https://tu-app.onrender.com`)

## 📝 Notas Importantes
- Este es un sitio estático que no requiere servidor
- Usa Tailwind CSS desde CDN
- Se conecta al backend via API REST
- Compatible con ambas plataformas sin modificaciones adicionales