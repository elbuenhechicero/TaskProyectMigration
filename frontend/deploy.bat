@echo off
echo ================================
echo   TASK MANAGER - DEPLOY SCRIPT
echo ================================
echo.

echo Verificando que estamos en la carpeta frontend...
if not exist "index.html" (
    echo ERROR: No se encontro index.html. Ejecuta este script desde la carpeta frontend.
    pause
    exit /b 1
)

echo ✅ Archivos del proyecto encontrados
echo.

echo Opciones de despliegue:
echo 1. Preparar para Vercel
echo 2. Preparar para Render  
echo 3. Verificar configuracion
echo 4. Abrir URLs de las plataformas
echo.

set /p "choice=Selecciona una opcion (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 DESPLIEGUE EN VERCEL:
    echo.
    echo Paso 1: Sube tu codigo a GitHub
    echo Paso 2: Ve a https://vercel.com
    echo Paso 3: Conecta tu repositorio
    echo Paso 4: Selecciona la carpeta 'frontend' como directorio raiz
    echo Paso 5: Vercel detectara automaticamente la configuracion
    echo.
    echo ¿Quieres abrir Vercel en el navegador? (s/n^)
    set /p "open=: "
    if /i "%open%"=="s" start https://vercel.com
) else if "%choice%"=="2" (
    echo.
    echo 🚀 DESPLIEGUE EN RENDER:
    echo.
    echo Opcion A - Usando Blueprint:
    echo   1. Ve a https://render.com
    echo   2. New ^> Blueprint
    echo   3. Conecta tu repositorio
    echo   4. Render usara el archivo render.yaml
    echo.
    echo Opcion B - Static Site:
    echo   1. Ve a https://render.com  
    echo   2. New ^> Static Site
    echo   3. Root Directory: frontend
    echo   4. Build Command: echo "Build completed"
    echo   5. Publish Directory: .
    echo.
    echo ¿Quieres abrir Render en el navegador? (s/n^)
    set /p "open=: "
    if /i "%open%"=="s" start https://render.com
) else if "%choice%"=="3" (
    echo.
    echo 🔍 VERIFICACION DE CONFIGURACION:
    echo.
    if exist "package.json" (echo ✅ package.json encontrado) else (echo ❌ package.json no encontrado)
    if exist "vercel.json" (echo ✅ vercel.json encontrado) else (echo ❌ vercel.json no encontrado)  
    if exist "render.yaml" (echo ✅ render.yaml encontrado) else (echo ❌ render.yaml no encontrado)
    if exist "index.html" (echo ✅ index.html encontrado) else (echo ❌ index.html no encontrado)
    if exist "js\config.js" (echo ✅ config.js encontrado) else (echo ❌ config.js no encontrado)
    echo.
    echo API URL configurada:
    findstr "API_BASE_URL" js\config.js
    echo.
) else if "%choice%"=="4" (
    echo.
    echo 🌐 Abriendo plataformas de despliegue...
    start https://vercel.com
    start https://render.com
    start https://github.com
) else (
    echo Opcion no valida.
)

echo.
echo ================================
echo     DESPLIEGUE COMPLETADO
echo ================================
pause