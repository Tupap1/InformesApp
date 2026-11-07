"""
Servicio de Reportes
Lógica de negocio para generación de reportes
"""

# Por ahora, importa las funciones del archivo reports.py original
# TODO: Migrar completamente la lógica aquí
from reports import (
    reporte_productos_vendidos,
    reporte_utilidad
)
from app.models import Artic, Pas, Proveedo
from sqlalchemy import and_
from datetime import datetime


def reporte_inventario(db, filtros):
    """Genera reporte de inventario con filtros"""
    query = db.session.query(
        Artic,
        Pas.PASNOM.label('nombre_producto'),
        Pas.PASOBSERVA.label('descripcion_producto'),
        Proveedo.PROCON.label('nombre_proveedor')
    ).outerjoin(
        Pas, Artic.ARTCOD == Pas.PAS
    ).outerjoin(
        Proveedo, Artic.PROCODIGO == Proveedo.PROCOD
    )
    
    # Aplicar filtros
    conditions = []
    
    if filtros.get('codigo'):
        conditions.append(Artic.ARTCOD.like(f'%{filtros["codigo"]}%'))
    if filtros.get('sucursal'):
        conditions.append(Artic.SUCCOD == filtros['sucursal'])
    if filtros.get('proveedor'):
        conditions.append(Artic.PROCODIGO == filtros['proveedor'])
    if filtros.get('estado'):
        conditions.append(Artic.PASESTADO == filtros['estado'])
    else:
        conditions.append(Artic.PASESTADO == 'ACT')
    if filtros.get('ubicacion'):
        conditions.append(Artic.UBICODIGO == filtros['ubicacion'])
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    query = query.order_by(Artic.ARTCOD)
    resultados = query.all()
    
    # Formatear resultados
    items = []
    for artic, nombre_producto, descripcion_producto, nombre_proveedor in resultados:
        item = artic.to_dict()
        item['nombreProducto'] = nombre_producto or 'N/A'
        item['descripcionProducto'] = descripcion_producto or 'N/A'
        item['nombreProveedor'] = nombre_proveedor or 'N/A'
        item['valorInventario'] = artic.ARTEXI * artic.ARTCPR
        item['valorInventarioPrecio'] = artic.ARTEXI * artic.ARTPRE
        item['disponible'] = artic.ARTEXI - artic.ARTSEP
        item['alertas'] = {
            'bajoPuntoMinimo': artic.ARTEXI < artic.ARTPUNMIN if artic.ARTPUNMIN > 0 else False,
            'puntoReorden': artic.ARTEXI <= artic.ARTPUNPED if artic.ARTPUNPED > 0 else False,
            'sobreMaximo': artic.ARTEXI > artic.ARTPUNMAX if artic.ARTPUNMAX > 0 else False
        }
        items.append(item)
    
    total_items = len(items)
    total_existencias = sum(item['existencia'] for item in items)
    total_valor_costo = sum(item['valorInventario'] for item in items)
    total_valor_venta = sum(item['valorInventarioPrecio'] for item in items)
    
    return {
        'tipo': 'inventario',
        'fecha_generacion': datetime.now().isoformat(),
        'filtros_aplicados': filtros,
        'estadisticas': {
            'totalItems': total_items,
            'totalExistencias': total_existencias,
            'valorTotalCosto': round(total_valor_costo, 2),
            'valorTotalVenta': round(total_valor_venta, 2),
            'utilidadPotencial': round(total_valor_venta - total_valor_costo, 2)
        },
        'datos': items
    }


def reporte_ventas(db, filtros):
    """Genera reporte de ventas - delegado a reports.py"""
    from reports import crear_modelo_venta, crear_modelo_dventa, determinar_año_desde_filtros
    # Implementación compleja - mantener en reports.py por ahora
    pass


def detalle_venta(db, numero_venta, filtros):
    """Obtiene detalle de una venta específica"""
    from reports import crear_modelo_dventa, determinar_año_desde_filtros
    # Implementación - mantener en reports.py por ahora
    pass
