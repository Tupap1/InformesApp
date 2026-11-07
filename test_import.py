"""Script de prueba para diagnosticar imports"""
import sys
import traceback

try:
    print("Importando Flask...")
    from flask import Flask
    print("✓ Flask OK")
    
    print("Importando Flask-CORS...")
    from flask_cors import CORS
    print("✓ Flask-CORS OK")
    
    print("Importando Flask-SQLAlchemy...")
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Flask-SQLAlchemy OK")
    
    print("Importando app...")
    sys.path.insert(0, 'backend')
    from app import create_app
    print(" OK app.create_app")
    
    print("\n¡Todos los imports funcionan!")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
    print(f"\nTraceback completo:")
    traceback.print_exc()
