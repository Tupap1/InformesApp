@echo off
echo ============================================================
echo   Deteniendo Sistema de Reportes
echo ============================================================
echo.

taskkill /F /IM SistemaReportes.exe >nul 2>&1

if %errorlevel% == 0 (
    echo [OK] Servidor detenido exitosamente
) else (
    echo [INFO] El servidor no estaba en ejecucion
)

echo.
echo Presione cualquier tecla para cerrar...
pause >nul
