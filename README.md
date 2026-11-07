# GReports Backend - Quick Start Guide

## Prerequisites
- Python 3.11+ installed
- MySQL 8.0 running
- Database `pv` accessible with credentials

## Setup Instructions

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update with your database credentials:
```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:
- `DB_HOST` - Your MySQL host (default: localhost)
- `DB_PASSWORD` - Your MySQL root password
- Other settings as needed

### 3. Start the Server
```powershell
uvicorn app.main:app --reload --port 8000
```

### 4. Verify Installation
Open your browser to:
- **API Root**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure
```
GReports/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── core/
│   │   └── config.py        # Pydantic settings
│   ├── db/
│   │   └── session.py       # Async SQLAlchemy session
│   ├── models/
│   │   ├── base.py          # Declarative base
│   │   ├── inventory.py     # Artic model
│   │   └── dynamic_sales.py # Venta/Dvent factory
│   ├── schemas/
│   │   ├── inventory.py     # Pydantic schemas
│   │   └── health.py        # Health check schema
│   └── api/
│       └── health.py        # Health router
├── requirements.txt
├── .env.example
└── README.md
```

## Testing the Health Endpoint

### Using curl
```powershell
curl http://localhost:8000/health
```

### Expected Response
```json
{
  "status": "healthy",
  "database_connected": true,
  "timestamp": "2026-02-03T20:00:00",
  "message": "All systems operational"
}
```

## Next Steps (Phase 2)
- Implement inventory reports endpoint
- Add sales reports with dynamic year handling
- Create profit/utility calculations
- Add data export (Excel/PDF)

## Troubleshooting

### Database Connection Failed
- Verify MySQL is running
- Check credentials in `.env`
- Ensure database `pv` exists
- Test connection: `mysql -u root -p pv`

### Import Errors
- Ensure you're in the project root directory
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

### Port Already in Use
- Change port: `uvicorn app.main:app --reload --port 8001`
