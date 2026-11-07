"""
Manejadores de Errores Globales
"""

from flask import jsonify
import traceback
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Registra manejadores de errores globales"""
    
    @app.errorhandler(Exception)
    def handle_error(e):
        """Maneja todos los errores y devuelve respuesta JSON"""
        error_traceback = traceback.format_exc()
        
        logger.error(f"ERROR: {type(e).__name__}: {str(e)}")
        logger.error(f"Traceback:\n{error_traceback}")
        
        return jsonify({
            'error': f'{type(e).__name__}: {str(e)}',
            'tipo': type(e).__name__,
            'mensaje': str(e),
            'solucion': 'Verifique la conexión a MySQL y que las credenciales sean correctas'
        }), 500
