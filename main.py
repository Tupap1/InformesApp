"""
Sistema de Reportes - Punto de Entrada Principal
Inicia el servidor Flask con Waitress en modo produccion
"""

import os
import sys
import webbrowser
import time
import threading
import logging
from datetime import datetime


def crear_env_default():
    """Crea un archivo .env con valores por defecto si no existe"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')

    if not os.path.exists(env_path):
        default_content = """# Configuracion de la Base de Datos MySQL
# Formato: mysql+mysqlconnector://usuario:contrasena@host:puerto/nombre_base_datos
DATABASE_URI=mysql+mysqlconnector://root:@localhost:3306/pv

# Puerto del servidor Flask
PORT=5000

# Servidor y threads para Waitress
HOST=0.0.0.0
THREADS=4

# Modo Debug (True para desarrollo, False para produccion)
FLASK_DEBUG=False

# Habilitar log de consultas SQL (True para ver queries, False para ocultar)
SQL_DEBUG=False
"""
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
        except Exception as e:
            # Si falla, no hay problema, se usarán las variables de entorno por defecto
            pass


def configurar_logging():
    """Configura el sistema de logging"""
    # Crear carpeta de logs en AppData del usuario para evitar problemas de permisos
    appdata = os.environ.get('APPDATA', os.path.dirname(__file__))
    log_dir = os.path.join(appdata, 'SistemaReportes', 'logs')

    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        # Si falla, usar carpeta temporal
        log_dir = os.path.join(os.environ.get('TEMP', '.'), 'SistemaReportes', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    # Nombre del archivo de log con fecha
    log_file = os.path.join(log_dir, f'reportes_{datetime.now().strftime("%Y%m%d")}.log')

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger('SistemaReportes')
    logger.info("="*60)
    logger.info("Sistema de Reportes iniciado")
    logger.info(f"Archivo de log: {log_file}")
    logger.info("="*60)

    return logger


def iniciar_servidor():
    """Inicia el servidor Flask con Waitress (producción)"""
    try:
        from dotenv import load_dotenv

        # Cargar .env con codificación UTF-8 explícita para evitar errores en Windows
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path, encoding='utf-8')

        # Configurar logging
        logger = configurar_logging()

        logger.info("Cargando módulos del servidor...")

        # Importar el módulo del servidor
        import server
        from waitress import serve

        # Obtener configuración
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        threads = int(os.getenv('THREADS', 4))

        # Obtener ubicación de logs
        appdata = os.environ.get('APPDATA', os.path.dirname(__file__))
        log_location = os.path.join(appdata, 'SistemaReportes', 'logs')

        logger.info("="*60)
        logger.info("Servidor de Producción - Sistema de Reportes")
        logger.info("="*60)
        logger.info(f"Servidor: Waitress (Producción)")
        logger.info(f"Puerto: {port}")
        logger.info(f"Host: {host}")
        logger.info(f"Threads: {threads}")
        logger.info(f"Base de datos: MySQL (SQLAlchemy)")
        logger.info(f"Logs: {log_location}")
        logger.info("="*60)
        logger.info(f"Iniciando Waitress en {host}:{port} con {threads} threads")

        # Iniciar servidor Waitress (headless, producción)
        serve(
            server.app,
            host=host,
            port=port,
            threads=threads,
            url_scheme='http',
            _quiet=False
        )

    except Exception as e:
        logger = logging.getLogger('SistemaReportes')
        logger.error(f"ERROR al iniciar el servidor: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")


def abrir_navegador():
    """Abre el navegador después de que el servidor inicie"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass


if __name__ == '__main__':
    try:
        # Crear .env con valores por defecto si no existe
        # (El instalador de Inno Setup ya lo crea, esto es solo para instalaciones manuales)
        crear_env_default()

        # Abrir navegador en hilo separado
        browser_thread = threading.Thread(target=abrir_navegador, daemon=True)
        browser_thread.start()

        # Iniciar servidor headless
        iniciar_servidor()

    except KeyboardInterrupt:
        logger = logging.getLogger('SistemaReportes')
        logger.info("Servidor detenido por el usuario")

    except Exception as e:
        logger = logging.getLogger('SistemaReportes')
        logger.error(f"ERROR CRÍTICO: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback:\n{traceback.format_exc()}")
