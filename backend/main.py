"""
Backend - Punto de Entrada Principal
Inicia el servidor Flask con Waitress
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, encoding='utf-8')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('SistemaReportes')

# Importar app
from app import create_app

# Crear aplicación
app = create_app()


def run_server():
    """Ejecuta el servidor en modo desarrollo o producción"""
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    if os.getenv('FLASK_ENV') == 'development':
        # Modo desarrollo - Flask development server
        logger.info("Iniciando en modo DESARROLLO")
        app.run(host=host, port=port, debug=True)
    else:
        # Modo producción - Waitress
        from waitress import serve
        threads = int(os.getenv('THREADS', 4))
        
        logger.info("="*60)
        logger.info("Servidor de Producción - Sistema de Reportes")
        logger.info("="*60)
        logger.info(f"Host: {host}:{port}")
        logger.info(f"Threads: {threads}")
        logger.info("="*60)
        
        serve(app, host=host, port=port, threads=threads, url_scheme='http')


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("\nServidor detenido por el usuario")
    except Exception as e:
        logger.error(f"ERROR CRÍTICO: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)
