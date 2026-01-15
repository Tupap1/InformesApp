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


def crear_archivo_error(tipo_error, mensaje):
    """Crea un archivo de error visible en el escritorio del usuario"""
    try:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        error_file = os.path.join(desktop, 'ERROR_SistemaReportes.txt')

        with open(error_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("ERROR AL INICIAR SISTEMA DE REPORTES\n")
            f.write("="*60 + "\n\n")
            f.write(f"Tipo de Error: {tipo_error}\n\n")
            f.write(f"Mensaje:\n{mensaje}\n\n")
            f.write("="*60 + "\n")
            f.write("SOLUCIÓN:\n")
            f.write("="*60 + "\n\n")
            f.write("Revise los logs en:\n")
            appdata = os.environ.get('APPDATA', 'C:\\Users\\[Usuario]\\AppData\\Roaming')
            f.write(f"{appdata}\\SistemaReportes\\logs\\reportes_[FECHA].log\n\n")
            f.write("Si el problema persiste, contacte al soporte técnico.\n")
    except:
        pass  # Si no se puede crear el archivo, no hay problema


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
    logger = None
    try:
        from dotenv import load_dotenv

        # Cargar .env con codificación UTF-8 explícita para evitar errores en Windows
        env_path = os.path.join(os.path.dirname(__file__), '.env')

        # Verificar si .env existe
        if os.path.exists(env_path):
            load_dotenv(env_path, encoding='utf-8')
        else:
            # Si no existe, crear uno por defecto
            crear_env_default()
            load_dotenv(env_path, encoding='utf-8')

        # Configurar logging
        logger = configurar_logging()

        logger.info("Cargando módulos del servidor...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Ejecutable: {sys.executable}")
        logger.info(f"Directorio de trabajo: {os.getcwd()}")

        # Obtener configuración ANTES de importar módulos
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        threads = int(os.getenv('THREADS', 4))
        database_uri = os.getenv('DATABASE_URI', 'mysql+mysqlconnector://root:@localhost:3306/pv')

        logger.info(f"Configuración cargada desde .env:")
        logger.info(f"  PORT: {port}")
        logger.info(f"  HOST: {host}")
        logger.info(f"  THREADS: {threads}")
        # Ocultar contraseña en logs
        db_uri_safe = database_uri.split('@')[0].split('://')[0] + '://***@' + database_uri.split('@')[1] if '@' in database_uri else database_uri
        logger.info(f"  DATABASE_URI: {db_uri_safe}")

        # Importar el módulo del servidor
        logger.info("Importando módulo server.py...")
        import server
        logger.info("✓ Módulo server.py importado correctamente")

        logger.info("Importando Waitress...")
        from waitress import serve
        logger.info("✓ Waitress importado correctamente")

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
        logger.info("La aplicación está lista. Acceda en: http://localhost:5000")

        # Iniciar servidor Waitress (headless, producción)
        serve(
            server.app,
            host=host,
            port=port,
            threads=threads,
            url_scheme='http',
            _quiet=False
        )

    except ImportError as e:
        error_msg = f"ERROR DE IMPORTACIÓN: {str(e)}\nFaltan dependencias. La aplicación no puede iniciar."

        if logger:
            logger.error(f"ERROR DE IMPORTACIÓN: {str(e)}")
            logger.error("Faltan dependencias. La aplicación no puede iniciar.")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        else:
            print(error_msg)

        # Crear archivo de error visible en el escritorio
        crear_archivo_error("ImportError", str(e))
        sys.exit(1)

    except Exception as e:
        error_msg = f"ERROR al iniciar el servidor: {type(e).__name__}: {str(e)}"

        if logger:
            logger.error(error_msg)
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        else:
            print(error_msg)
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")

        # Crear archivo de error visible en el escritorio
        crear_archivo_error(type(e).__name__, str(e))
        sys.exit(1)


def abrir_navegador():
    """Abre el navegador después de que el servidor inicie"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass


if __name__ == '__main__':
    try:
        print("="*60)
        print("Sistema de Reportes - Iniciando...")
        print("="*60)

        # Crear .env con valores por defecto si no existe
        # (El instalador de Inno Setup ya lo crea, esto es solo para instalaciones manuales)
        crear_env_default()

        # Abrir navegador en hilo separado
        browser_thread = threading.Thread(target=abrir_navegador, daemon=True)
        browser_thread.start()

        # Iniciar servidor headless
        iniciar_servidor()

    except KeyboardInterrupt:
        try:
            logger = logging.getLogger('SistemaReportes')
            logger.info("Servidor detenido por el usuario")
        except:
            print("\nServidor detenido por el usuario")

    except Exception as e:
        try:
            logger = logging.getLogger('SistemaReportes')
            logger.error(f"ERROR CRÍTICO: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
        except:
            print(f"\nERROR CRÍTICO: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")

        # Crear archivo de error visible en el escritorio
        crear_archivo_error(type(e).__name__, str(e))
        sys.exit(1)
