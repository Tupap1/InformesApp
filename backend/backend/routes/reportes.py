"""
Blueprint: Reportes
Endpoints para generación de reportes (inventario, ventas, etc.)
"""

from flask import Blueprint, request, jsonify, send_file
from app.services import reporte_service, export_service
from app.models import Pas, Artic
from app import db

bp = Blueprint('reportes', __name__, url_prefix='/api')


@bp.route('/reportes', methods=['GET'])
def get_reportes():
    """
    Endpoint principal para obtener reportes
    
    Query params:
    - tipo: Tipo de reporte ('inventario', 'ventas')
    - codigo, sucursal, proveedor, fechaInicio, fechaFin, estado, ubicacion
    """
    try:
        tipo_reporte = request.args.get('tipo', 'inventario')
        
        # Extraer filtros
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin'),
            'estado': request.args.get('estado'),
            'ubicacion': request.args.get('ubicacion')
        }
        
        if tipo_reporte == 'inventario':
            resultado = reporte_service.reporte_inventario(db, filtros)
        elif tipo_reporte == 'ventas':
            filtros['incluir_narradas'] = request.args.get('incluir_narradas', 'false').lower() == 'true'
            filtros['detalle_productos'] = request.args.get('detalle_productos', 'false').lower() == 'true'
            resultado = reporte_service.reporte_ventas(db, filtros)
        else:
            return jsonify({
                'error': f'Tipo de reporte no soportado: {tipo_reporte}',
                'tipos_validos': ['inventario', 'ventas']
            }), 400
        
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el reporte',
            'detalle': str(e)
        }), 500


@bp.route('/reportes/productos-vendidos', methods=['GET'])
def get_productos_vendidos():
    """Endpoint para reporte de productos vendidos"""
    try:
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'grupo': request.args.get('grupo'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin')
        }
        
        resultado = reporte_service.reporte_productos_vendidos(db, Pas, Artic, filtros)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el reporte de productos vendidos',
            'detalle': str(e)
        }), 500


@bp.route('/reportes/utilidad', methods=['GET'])
def get_utilidad():
    """Endpoint para reporte de utilidad/ganancias"""
    try:
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'grupo': request.args.get('grupo'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin')
        }
        
        resultado = reporte_service.reporte_utilidad(db, Pas, Artic, filtros)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el reporte de utilidad',
            'detalle': str(e)
        }), 500


@bp.route('/detalle_venta/<numero_venta>', methods=['GET'])
def get_detalle_venta(numero_venta):
    """
    Obtener detalle de productos de una venta específica
    """
    try:
        fecha_inicio = request.args.get('fechaInicio')
        fecha_fin = request.args.get('fechaFin')
        
        filtros = {
            'fechaInicio': fecha_inicio,
            'fechaFin': fecha_fin
        }
        
        resultado = reporte_service.detalle_venta(db, numero_venta, filtros)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/exportar/excel', methods=['POST'])
def exportar_excel():
    """Exportar reporte a Excel"""
    try:
        data = request.json
        tipo_reporte = data.get('tipo_reporte')
        datos_reporte = data.get('datos')
        
        archivo = export_service.exportar_excel(datos_reporte, tipo_reporte)
        
        return send_file(
            archivo,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'reporte_{tipo_reporte}.xlsx'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/exportar/pdf', methods=['POST'])
def exportar_pdf():
    """Exportar reporte a PDF"""
    try:
        data = request.json
        tipo_reporte = data.get('tipo_reporte')
        datos_reporte = data.get('datos')
        
        archivo = export_service.exportar_pdf(datos_reporte, tipo_reporte)
        
        return send_file(
            archivo,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'reporte_{tipo_reporte}.pdf'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
