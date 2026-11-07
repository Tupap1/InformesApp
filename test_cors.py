"""Script de prueba para diagnosticar Flask-CORS"""
import sys
import traceback

try:
    print("Importando Flask...")
    from flask import Flask
    print("✓ Flask OK\n")
    
    print("Importando Flask-CORS...")
    from flask_cors import CORS
    print("✓ Flask-CORS OK")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}\n")
    print(f"Traceback completo:\n")
    traceback.print_exc()
