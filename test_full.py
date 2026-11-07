"""Script de prueba completo"""
import sys
import os
import traceback

# Cargar variables de entorno
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, encoding='utf-8')

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

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
    from app import create_app
    print("✓ app.create_app OK")
    
    print("\nCreando aplicación...")
    app = create_app()
    print("✓ Aplicación creada OK")
    
    print("\n¡TODO OK! Iniciando servidor...")
    app.run(debug=True, port=5000)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}\n")
    print("Traceback completo:\n")
    traceback.print_exc()
