# InformesApp

Desktop report generator built for Gsigma — packages a Python data/reporting backend with a React frontend into a single installable Windows app, so non-technical store staff can generate reports without touching a terminal.

## Stack
- **Python** (`server.py`, `reports.py`) for data processing and report generation
- **React + Vite + Tailwind** frontend
- Packaged as a standalone Windows installer via **PyInstaller** (`reportes.spec`) and Inno Setup (`installer.iss`) — bundles a Python runtime so end users never install Python themselves

## Why it's interesting
Most "desktop app" tutorials stop at Electron + a web frontend. This one solves the harder packaging problem: bundling a Python backend and a JS frontend into one double-click installer for non-technical end users.
