"""
Blueprint: Health Check
Endpoint para verificar que el servidor está funcionando
"""

from flask import Blueprint, jsonify
from datetime import datetime

bp = Blueprint('health', __name__)


@bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar que el servidor está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Servidor de reportes funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })
