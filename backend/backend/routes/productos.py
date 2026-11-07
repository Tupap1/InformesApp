"""
Blueprint: Productos
Endpoints para gestión de productos (búsquedas, listados, etc.)
"""

from flask import Blueprint, request, jsonify
from app.models import Artic, Pas, Proveedo
from app import db
from sqlalchemy import or_

bp = Blueprint('productos', __name__, url_prefix='/api')


@bp.route('/productos/buscar', methods=['GET'])
def buscar_productos():
    """
    Búsqueda de productos por código o nombre
    
    Query params:
    - q: término de búsqueda
    - limit: límite de resultados (default: 50)
    """
    try:
        query_str = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not query_str:
            return jsonify({'productos': []}), 200
        
        # Buscar por código o nombre
        productos = db.session.query(
            Artic, 
            Pas.PASNOM.label('nombre')
        ).outerjoin(
            Pas, Artic.ARTCOD == Pas.PAS
        ).filter(
            or_(
                Artic.ARTCOD.like(f'%{query_str}%'),
                Pas.PASNOM.like(f'%{query_str}%')
            )
        ).limit(limit).all()
        
        resultados = []
        for artic, nombre in productos:
            item = artic.to_dict()
            item['nombre'] = nombre or 'N/A'
            resultados.append(item)
        
        return jsonify({'productos': resultados})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """
    Listar todos los proveedores activos
    """
    try:
        proveedores = Proveedo.query.filter(
            Proveedo.status != 'I'  # No inactivos
        ).all()
        
        return jsonify({
            'proveedores': [p.to_dict() for p in proveedores]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
