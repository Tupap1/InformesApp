# InformesApp — Suite de Reportería Financiera, Analítica y Dashboard POS

> **Repositorio GitHub:** `https://github.com/Tupap1/InformesApp`  
> **Visibilidad:** Public  
> **Carpetas Locales:** `C:\Proyectos\Informes` (Workspace Completo con Docker/Electron) y `C:\Proyectos\InformesApp` (Workspace de Empaquetado e Instalador)  
> **Estado:** Producción / Instalador Distribuido  

---

## Overview

**InformesApp** es una suite de analítica comercial, reportería financiera y control de márgenes para empresas del sector retail que operan con sistemas de punto de venta tradicionales. Proporciona a gerentes y contadores paneles visuales interactivos, cálculo de utilidades reales, auditoría de cajeros y exportación masiva de estados financieros a Excel y PDF sin requerir modificaciones en el software POS existente.

---

## Architecture

Aplicación híbrida con soporte para ejecución como aplicación de escritorio autónoma (Electron/Inno Setup), servidor web local o contenedor Docker:

```
 ┌────────────────────────────────────────────────────────┐
 │                    InformesApp Desktop                 │
 │  ┌───────────────────────┐   ┌──────────────────────┐  │
 │  │ Frontend Web (React/  │   │ Servidor API Local   │  │
 │  │ Vite / Tailwind CSS)  │◄─►│ (FastAPI / Python)   │  │
 │  └───────────────────────┘   └──────────┬───────────┘  │
 └─────────────────────────────────────────┼──────────────┘
                                           │ SQL Queries
                                           ▼
 ┌────────────────────────────────────────────────────────┐
 │            Base de Datos POS de la Tienda              │
 │              (MySQL / MariaDB / SQL Server)            │
 └────────────────────────────────────────────────────────┘
```

### Decisiones de Diseño Clave:
1. **Doble Modalidad de Despliegue:** Soporta ejecución de escritorio con Electron y empaquetado Inno Setup (`installer.iss`), y ejecución como servicio multiusuario con Docker Compose (`docker-compose.yml`).
2. **Cálculo de Utilidad Real en Tiempo de Ejecución:** Mapeo relacional de compras (`MAPEO_DE_DATOS.md`) contra salidas de venta para obtener márgenes brutos y netos por referencia.
3. **Manejo de Errores y Resiliencia CORS:** Módulo centralizado `backend/app/utils/error_handlers.py` y configuración de orígenes locales para prevenir bloqueos de comunicación en el cliente.

---

## Tech Stack

### Dependencias Principales Confirmadas en Código
- **Backend API:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pandas, OpenPyXL, PyMySQL, `reports.py`, `server.py`
- **Frontend UI:** React, Vite, Tailwind CSS, PostCSS, Lucide React
- **Desktop Wrapper:** Electron (`electron/preload.js`, `electron-builder.yml`)
- **Empaquetador de Windows:** Inno Setup (`installer.iss`, `installer_simple.iss`), PyInstaller (`reportes.spec`, `reportes_onefile.spec`)
- **Infraestructura:** Docker (`docker-compose.yml`, `backend/Dockerfile`), scripts de automatización PowerShell (`dev.ps1`, `build.ps1`, `organize-for-docker.ps1`)

---

## Key Features

- **Dashboard Ejecutivo:** Métricas de ventas del día, ticket promedio, artículos más vendidos y comparación con períodos anteriores.
- **Reportes Financieros Detallados:** Ventas por departamento, comisiones de vendedores, formas de pago y cálculo de IVA discriminado.
- **Análisis de Rentabilidad:** Márgenes de ganancia por línea de producto y alertas de ítems con margen negativo o nulo.
- **Exportación Inmediata:** Descarga de reportes tabulares en formato Microsoft Excel (XLSX) con fórmulas y formatos contables.
- **Instalador de Escritorio con Un Clic:** Ejecutable de Windows que configura automáticamente el servicio local.

---

## Setup & Run

### Requisitos Previos
- Python 3.10+
- Node.js 18+
- Base de datos comercial (MySQL / MariaDB)

### Ejecutar en Desarrollo (PowerShell)
```powershell
# Iniciar frontend y backend coordinados
.\dev.ps1
```

### Ejecutar con Docker Compose
```bash
docker compose up -d --build
# Acceder en http://localhost:8000 o puerto asignado
```

### Compilar Instalador de Windows
```powershell
.uild.ps1
# Compilar instalador final con Inno Setup:
iscc installer.iss
```

---

## Status

- **Fase Actual:** Producción activa.
- **Evidencia en Código:** Instalador Inno Setup (`installer.iss`), documentación de transferencia de conocimiento (`knowledge_transfer.md`), especificación de datos (`MAPEO_DE_DATOS.md`) y commits de soporte a clientes comerciales.
