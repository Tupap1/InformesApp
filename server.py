"""
Flask Server para Sistema de Reportes de Inventario y Ventas
Utiliza SQLAlchemy ORM para conectarse a MySQL
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, and_, or_, func, distinct
from datetime import datetime
import os
from dotenv import load_dotenv

# Importar módulo de reportes
from reports import (
    reporte_productos_vendidos,
    reporte_utilidad,
    exportar_a_excel,
    exportar_a_pdf
)

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URI',
    'mysql+mysqlconnector://root:password@localhost:3306/pv'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQL_DEBUG', 'False') == 'True'

# Inicializar SQLAlchemy
db = SQLAlchemy(app)


# ========================================
# MODELOS DE BASE DE DATOS
# ========================================

class Artic(db.Model):
    """
    Modelo para la tabla ARTIC (Inventario de Productos)
    Representa el inventario principal de artículos en cada sucursal
    """
    __tablename__ = 'artic'

    # Clave primaria compuesta
    SUCCOD = db.Column(db.String(2), primary_key=True, nullable=False, default='')
    ARTCOD = db.Column(db.String(15), primary_key=True, nullable=False, default='')
    EMPID = db.Column(db.String(20), primary_key=True, nullable=False, default='')

    # Información de existencias y fechas
    ARTEXI = db.Column(db.Float, nullable=False, default=0)  # Existencia
    ARTFEC = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Fecha última compra
    ARTFIS = db.Column(db.Float, nullable=False, default=0)  # Inventario físico
    ARTSEP = db.Column(db.Float, nullable=False, default=0)  # Cantidad separada

    # Información de costos y precios
    ARTCOS = db.Column(db.Float, nullable=False, default=0)  # Costo
    ARTCPR = db.Column(db.Float, nullable=False, default=0)  # Costo promedio
    ARTPRE = db.Column(db.Float, nullable=False, default=0)  # Precio de venta
    ARTPREPREV = db.Column(db.Boolean, nullable=False, default=False)  # Precio preventa
    PASPREBAS = db.Column(db.Float, nullable=False, default=0)  # Precio base

    # Información de IVA y porcentajes
    ARTIVA = db.Column(db.Float, nullable=False, default=0)  # IVA
    ARTPORCENT = db.Column(db.Float, nullable=False, default=0)  # Porcentaje de ganancia
    ARTREAPORC = db.Column(db.Float, nullable=False, default=0)  # Porcentaje de reajuste
    PASPORCOS = db.Column(db.Float, nullable=False, default=0)  # Porcentaje sobre costo

    # Puntos de pedido y máximos/mínimos
    ARTPUNMAX = db.Column(db.Float, nullable=False, default=0)  # Punto máximo
    ARTPUNPED = db.Column(db.Float, nullable=False, default=0)  # Punto de pedido
    ARTPUNMIN = db.Column(db.Float, nullable=False, default=0)  # Punto mínimo

    # Información del proveedor
    PROCODIGO = db.Column(db.String(15), nullable=False, default='')  # Código proveedor
    PROCOMPRA = db.Column(db.String(15), nullable=False, default='')  # Proveedor de compra

    # Estado y clasificación
    PASESTADO = db.Column(db.String(3), nullable=False, default='')  # Estado del producto
    PASCLASE = db.Column(db.String(1), nullable=False, default='')  # Clasificación
    PASTRATIP = db.Column(db.String(1), nullable=False, default='')  # Tipo de transacción

    # Ubicación y otras configuraciones
    UBICODIGO = db.Column(db.String(5), nullable=False, default='')  # Código de ubicación
    ARTOBSERVA = db.Column(db.String(240), nullable=False, default='')  # Observaciones

    # Fechas de control
    PASCREADO = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Fecha creación
    PASULTMOV = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Último movimiento
    PASULTMOD = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Última modificación
    ARTMODPRE = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Modificación precio

    # Otras configuraciones
    PASVENDIDO = db.Column(db.Float, nullable=False, default=0)  # Cantidad vendida
    PASCOMTIP = db.Column(db.Float, nullable=False, default=0)  # Tipo comisión
    ARTTIEMPOG = db.Column(db.Float, nullable=False, default=0)  # Tiempo garantía
    COMFC = db.Column(db.Float, nullable=False, default=0)  # Factor conversión
    PASOLECON = db.Column(db.String(20), nullable=False, default='')
    PASOLESET = db.Column(db.Boolean, nullable=False, default=False)
    PASCONFIS = db.Column(db.Boolean, nullable=False, default=False)
    PASUTIMIN = db.Column(db.Float, nullable=False, default=0)  # Utilidad mínima
    PASUTIMAX = db.Column(db.Float, nullable=False, default=0)  # Utilidad máxima
    PASPRO = db.Column(db.Boolean, nullable=False, default=False)  # Es producción
    PASDEV = db.Column(db.Boolean, nullable=False, default=False)  # Permite devolución
    PASULTMOS = db.Column(db.Float, nullable=False, default=0)
    PASUND = db.Column(db.Float, nullable=False, default=0)  # Unidades
    PASPUN = db.Column(db.Float, nullable=False, default=0)  # Puntos
    PASNEG = db.Column(db.Boolean, nullable=False, default=False)  # Negativo permitido
    PASPUNCRI = db.Column(db.String(1), nullable=False, default='')
    PASMODPRE = db.Column(db.Boolean, nullable=False, default=False)
    TABTIPNEG = db.Column(db.String(1), nullable=False, default='')
    ARTMODPRS = db.Column(db.Float, nullable=False, default=0)
    PASVALMAX = db.Column(db.Float, nullable=False, default=0)
    PASCOMI = db.Column(db.Float, nullable=False, default=0)
    unidexis = db.Column(db.Float, nullable=False, default=0)  # Unidades en existencia

    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'codigo': self.ARTCOD,
            'sucursal': self.SUCCOD,
            'existencia': self.ARTEXI,
            'existenciaUnidades': self.unidexis,
            'inventarioFisico': self.ARTFIS,
            'cantidadSeparada': self.ARTSEP,
            'fechaUltimaCompra': self.ARTFEC.strftime('%Y-%m-%d') if self.ARTFEC else None,
            'costo': self.ARTCOS,
            'costoPromedio': self.ARTCPR,
            'precioVenta': self.ARTPRE,
            'precioBase': self.PASPREBAS,
            'iva': self.ARTIVA,
            'porcentajeGanancia': self.ARTPORCENT,
            'proveedor': self.PROCODIGO,
            'proveedorCompra': self.PROCOMPRA,
            'estado': self.PASESTADO,
            'clasificacion': self.PASCLASE,
            'ubicacion': self.UBICODIGO,
            'observaciones': self.ARTOBSERVA,
            'puntoMaximo': self.ARTPUNMAX,
            'puntoPedido': self.ARTPUNPED,
            'puntoMinimo': self.ARTPUNMIN,
            'fechaCreacion': self.PASCREADO.strftime('%Y-%m-%d') if self.PASCREADO else None,
            'ultimoMovimiento': self.PASULTMOV.strftime('%Y-%m-%d') if self.PASULTMOV else None,
            'cantidadVendida': self.PASVENDIDO
        }


class Articv(db.Model):
    """
    Modelo para la tabla ARTICV (Ventas de Artículos)
    Representa las transacciones de venta de artículos
    """
    __tablename__ = 'articv'

    # Clave primaria compuesta (sin definir PRIMARY KEY explícita)
    ARTCOD = db.Column(db.String(15), nullable=False, default='')
    SUCCOD = db.Column(db.String(2), nullable=False, default='')
    UBICODIGO = db.Column(db.String(5), nullable=False, default='')
    ARTFEC_VEN = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))
    ARVID = db.Column(db.String(10), primary_key=True, nullable=False, default='')

    # Información de precios y cantidades
    ARTPRE = db.Column(db.Float, nullable=False, default=0)  # Precio de venta
    ARTFIS = db.Column(db.Float, nullable=False, default=0)  # Cantidad vendida
    PASEXISTEN = db.Column(db.Float, nullable=False, default=0)  # Existencia después de venta

    # Información de control
    ARVFECHA = db.Column(db.Date, nullable=False, default=datetime(2000, 1, 1))  # Fecha de venta
    USUARIO = db.Column(db.String(5), nullable=False, default='')  # Usuario que realizó la venta
    hardware_id = db.Column(db.Integer, nullable=False, default=0)  # ID del hardware
    idpa = db.Column(db.Float, nullable=False, default=0)
    cfdregister = db.Column(db.Boolean, nullable=False, default=False)
    cantunidc = db.Column(db.Float, nullable=False, default=0)  # Cantidad en unidades
    tableid = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.ARVID,
            'codigo': self.ARTCOD,
            'sucursal': self.SUCCOD,
            'ubicacion': self.UBICODIGO,
            'fechaVencimiento': self.ARTFEC_VEN.strftime('%Y-%m-%d') if self.ARTFEC_VEN else None,
            'precioVenta': self.ARTPRE,
            'cantidadVendida': self.ARTFIS,
            'cantidadUnidades': self.cantunidc,
            'existenciaPost': self.PASEXISTEN,
            'fechaVenta': self.ARVFECHA.strftime('%Y-%m-%d') if self.ARVFECHA else None,
            'usuario': self.USUARIO
        }


class Pas(db.Model):
    """
    Modelo para la tabla PAS (Catálogo de Productos)
    Contiene la información descriptiva de los productos
    """
    __tablename__ = 'pas'

    PAS = db.Column(db.String(15), primary_key=True, nullable=False, default='')  # Código del producto
    PASNOM = db.Column(db.String(80), nullable=False, default='')  # Nombre del producto
    PASTIPO = db.Column(db.String(1), nullable=False, default='')  # Tipo de producto
    GRUPCODI = db.Column(db.String(20), nullable=False, default='')  # Grupo
    PASOBSERVA = db.Column(db.Text, nullable=False)  # Descripción del producto (longtext)
    PASOBSFAC = db.Column(db.Boolean, nullable=False, default=False)  # Observación en factura
    PROGRAMA = db.Column(db.String(30), nullable=False, default='')  # Programa
    PASVENPRE = db.Column(db.Boolean, nullable=False, default=False)  # Venta por precio
    PUCCOD = db.Column(db.String(15), nullable=False, default='')  # Código PUC
    PCODIGO = db.Column(db.String(10), nullable=False, default='')  # Código de precio
    PASEST = db.Column(db.Boolean, nullable=False, default=False)  # Estado
    PASMAR = db.Column(db.String(80), nullable=False, default='')  # Marca
    PASVENC = db.Column(db.Boolean, nullable=False, default=False)  # Tiene vencimiento
    PASBALA = db.Column(db.Boolean, nullable=False, default=False)  # Balanza
    PASFACT = db.Column(db.Boolean, nullable=False, default=False)  # Facturable
    PASCOMP = db.Column(db.Boolean, nullable=False, default=False)  # Comprable

    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'codigo': self.PAS,
            'nombre': self.PASNOM,
            'descripcion': self.PASOBSERVA,
            'tipo': self.PASTIPO,
            'grupo': self.GRUPCODI,
            'marca': self.PASMAR,
            'estado': self.PASEST
        }


class Proveedo(db.Model):
    """
    Modelo para la tabla PROVEEDO (Proveedores)
    Contiene la información de los proveedores
    """
    __tablename__ = 'proveedo'

    PROCOD = db.Column(db.String(20), primary_key=True, nullable=False, default='')  # Código del proveedor
    PROCON = db.Column(db.String(40), nullable=False, default='')  # Nombre del proveedor
    PUCCOD = db.Column(db.String(15), nullable=False, default='')  # Código PUC
    PROPLAENT = db.Column(db.Float, nullable=False, default=0)  # Plazo de entrega
    PROPAG = db.Column(db.String(100), nullable=False, default='')  # Forma de pago
    PRONUMDOC = db.Column(db.String(15), nullable=False, default='')  # Número documento
    PROTIPDOC = db.Column(db.String(1), nullable=False, default='')  # Tipo documento
    EMPID = db.Column(db.String(20), nullable=False, default='')  # ID empresa
    PROTEL2 = db.Column(db.String(40), nullable=False, default='')  # Teléfono 2
    PROTEL3 = db.Column(db.String(40), nullable=False, default='')  # Teléfono 3
    TABTIPNEG = db.Column(db.String(1), nullable=False, default='')  # Tipo negocio
    status = db.Column(db.String(1))  # Estado

    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'codigo': self.PROCOD,
            'nombre': self.PROCON,
            'numerodocumento': self.PRONUMDOC,
            'tipodocumento': self.PROTIPDOC,
            'telefono2': self.PROTEL2,
            'telefono3': self.PROTEL3,
            'status': self.status
        }


# ========================================
# RUTAS / ENDPOINTS
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar que el servidor está funcionando
    """
    return jsonify({
        'status': 'ok',
        'message': 'Servidor de reportes funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/reportes', methods=['GET'])
def get_reportes():
    """
    Endpoint principal para obtener reportes

    Parámetros de consulta (query params):
    - tipo: Tipo de reporte ('inventario', 'ventas', etc.)
    - codigo: Código del producto (opcional, para filtrar)
    - sucursal: Código de sucursal (opcional)
    - proveedor: Código del proveedor (opcional)
    - fechaInicio: Fecha de inicio (formato: YYYY-MM-DD)
    - fechaFin: Fecha de fin (formato: YYYY-MM-DD)
    - estado: Estado del producto (ACT, INA, etc.)
    - ubicacion: Código de ubicación
    """
    try:
        # Obtener parámetros de la consulta
        tipo_reporte = request.args.get('tipo', 'inventario')
        codigo = request.args.get('codigo', None)
        sucursal = request.args.get('sucursal', None)
        proveedor = request.args.get('proveedor', None)
        fecha_inicio = request.args.get('fechaInicio', None)
        fecha_fin = request.args.get('fechaFin', None)
        estado = request.args.get('estado', None)
        ubicacion = request.args.get('ubicacion', None)

        # Ejecutar el reporte según el tipo
        if tipo_reporte == 'inventario':
            resultado = reporte_inventario(
                codigo=codigo,
                sucursal=sucursal,
                proveedor=proveedor,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado,
                ubicacion=ubicacion
            )
        elif tipo_reporte == 'ventas':
            resultado = reporte_ventas(
                codigo=codigo,
                sucursal=sucursal,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                ubicacion=ubicacion
            )
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


# ========================================
# FUNCIONES DE LÓGICA DE REPORTES
# ========================================

def reporte_inventario(codigo=None, sucursal=None, proveedor=None,
                       fecha_inicio=None, fecha_fin=None, estado=None, ubicacion=None):
    """
    Genera el reporte de inventario con filtros opcionales

    Returns:
        dict: Diccionario con los datos del reporte en formato JSON
    """
    # Iniciar consulta base con JOIN a la tabla pas (nombre del producto) y proveedo (proveedor)
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

    # Aplicar filtros dinámicamente
    filtros = []

    if codigo:
        # Búsqueda parcial por código
        filtros.append(Artic.ARTCOD.like(f'%{codigo}%'))

    if sucursal:
        filtros.append(Artic.SUCCOD == sucursal)

    if proveedor:
        filtros.append(Artic.PROCODIGO == proveedor)

    if estado:
        filtros.append(Artic.PASESTADO == estado)
    else:
        # Por defecto, solo productos activos
        filtros.append(Artic.PASESTADO == 'ACT')

    if ubicacion:
        filtros.append(Artic.UBICODIGO == ubicacion)

    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            filtros.append(Artic.ARTFEC >= fecha_inicio_obj)
        except ValueError:
            pass  # Ignorar si la fecha es inválida

    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            filtros.append(Artic.ARTFEC <= fecha_fin_obj)
        except ValueError:
            pass  # Ignorar si la fecha es inválida

    # Aplicar todos los filtros a la consulta
    if filtros:
        query = query.filter(and_(*filtros))

    # Ordenar por código de artículo
    query = query.order_by(Artic.ARTCOD)

    # Ejecutar la consulta
    resultados = query.all()

    # Formatear los resultados
    items = []
    for artic, nombre_producto, descripcion_producto, nombre_proveedor in resultados:
        item = artic.to_dict()
        item['nombreProducto'] = nombre_producto or 'N/A'
        item['descripcionProducto'] = descripcion_producto or 'N/A'
        item['nombreProveedor'] = nombre_proveedor or 'N/A'

        # Calcular valores adicionales
        item['valorInventario'] = artic.ARTEXI * artic.ARTCPR  # Existencia * Costo Promedio
        item['valorInventarioPrecio'] = artic.ARTEXI * artic.ARTPRE  # Existencia * Precio Venta
        item['disponible'] = artic.ARTEXI - artic.ARTSEP  # Existencia - Separado

        # Indicadores de alerta
        item['alertas'] = {
            'bajoPuntoMinimo': artic.ARTEXI < artic.ARTPUNMIN if artic.ARTPUNMIN > 0 else False,
            'puntoReorden': artic.ARTEXI <= artic.ARTPUNPED if artic.ARTPUNPED > 0 else False,
            'sobreMaximo': artic.ARTEXI > artic.ARTPUNMAX if artic.ARTPUNMAX > 0 else False
        }

        items.append(item)

    # Calcular estadísticas del reporte
    total_items = len(items)
    total_existencias = sum(item['existencia'] for item in items)
    total_valor_costo = sum(item['valorInventario'] for item in items)
    total_valor_venta = sum(item['valorInventarioPrecio'] for item in items)

    return {
        'tipo': 'inventario',
        'fecha_generacion': datetime.now().isoformat(),
        'filtros_aplicados': {
            'codigo': codigo,
            'sucursal': sucursal,
            'proveedor': proveedor,
            'fechaInicio': fecha_inicio,
            'fechaFin': fecha_fin,
            'estado': estado,
            'ubicacion': ubicacion
        },
        'estadisticas': {
            'totalItems': total_items,
            'totalExistencias': total_existencias,
            'valorTotalCosto': round(total_valor_costo, 2),
            'valorTotalVenta': round(total_valor_venta, 2),
            'utilidadPotencial': round(total_valor_venta - total_valor_costo, 2)
        },
        'datos': items
    }


def reporte_ventas(codigo=None, sucursal=None, fecha_inicio=None, fecha_fin=None, ubicacion=None, incluir_narradas=False, detalle_productos=False):
    """
    Genera el reporte de ventas usando las tablas VENTA y DVENT

    Args:
        incluir_narradas (bool): Si True, incluye la columna VENNAR
        detalle_productos (bool): Si True, agrupa por producto; si False, agrupa por documento

    Returns:
        dict: Diccionario con los datos del reporte en formato JSON
    """
    # Determinar año desde los filtros de fecha
    from reports import determinar_año_desde_filtros, crear_modelo_venta, crear_modelo_dventa

    filtros_dict = {
        'fechaInicio': fecha_inicio,
        'fechaFin': fecha_fin
    }
    sufijo_año = determinar_año_desde_filtros(filtros_dict)

    print(f"[DEBUG VENTAS] Usando año: 20{sufijo_año}, tablas: venta{sufijo_año}, dvent{sufijo_año}")
    print(f"[DEBUG VENTAS] Opciones: incluir_narradas={incluir_narradas}, detalle_productos={detalle_productos}")

    # Crear modelos dinámicos
    Venta = crear_modelo_venta(sufijo_año, db)
    Dventa = crear_modelo_dventa(sufijo_año, db)

    # Construir query dinámicamente según opciones
    if detalle_productos:
        # Modo DETALLE: Agrupar por producto (DVECOD)
        select_fields = [
            Dventa.DVECOD.label('codigo_producto'),
            Pas.PASNOM.label('nombre_producto'),
            func.count(distinct(Venta.VENDOC)).label('numero_ventas'),
            func.sum(Dventa.DVECAN).label('cantidad_total'),
            func.avg(Dventa.DVEPRE).label('precio_promedio'),
            func.sum(Dventa.DVEVAL).label('valor_total'),
            func.sum(Dventa.DVEDESCUEN).label('descuento'),
            func.sum(Dventa.DVEIMP).label('impuesto')
        ]

        query = db.session.query(*select_fields).join(
            Venta, and_(
                Dventa.DVENUM == Venta.VENDOC,
                Dventa.TRNTIPO == Venta.TRNTIPO
            )
        ).outerjoin(
            Pas, Dventa.DVECOD == Pas.PAS
        )

        group_by_fields = [
            Dventa.DVECOD,
            Pas.PASNOM
        ]
    else:
        # Modo CABECERA: Agrupar por documento de venta (VENDOC)
        select_fields = [
            Venta.VENDOC.label('numero_documento'),
            Venta.TRNTIPO.label('tipo_transaccion'),
            Venta.VENFEC.label('fecha_venta'),
            Venta.VENHOR.label('hora_venta'),
            Venta.VENCLI.label('codigo_cliente'),
            Venta.VENNOM.label('nombre_cliente'),
            Venta.VENVAL.label('valor_total'),
            Venta.VENDES.label('descuento'),
            Venta.VENIMP.label('impuesto'),
            Venta.VENEST.label('estado'),
            Venta.FACELECESTA.label('fe'),
            (Venta.VENVAL - Venta.VENIMP).label('base_grabable'),
            Venta.SUCCOD.label('sucursal'),
            func.count(Dventa.DVECOD).label('cantidad_productos'),
            func.sum(Dventa.DVECAN).label('cantidad_total_vendida')
        ]

        # Agregar VENNAR solo si se solicita
        if incluir_narradas:
            select_fields.insert(11, Venta.VENNAR.label('unidades_narradas'))

        query = db.session.query(*select_fields).join(
            Dventa, and_(
                Venta.VENDOC == Dventa.DVENUM,
                Venta.TRNTIPO == Dventa.TRNTIPO
            )
        )

        group_by_fields = [
            Venta.VENDOC,
            Venta.TRNTIPO,
            Venta.VENFEC,
            Venta.VENHOR,
            Venta.VENCLI,
            Venta.VENNOM,
            Venta.VENVAL,
            Venta.VENDES,
            Venta.VENIMP,
            Venta.VENEST,
            Venta.FACELECESTA,
            Venta.SUCCOD
        ]

        if incluir_narradas:
            group_by_fields.insert(11, Venta.VENNAR)

    query = query.group_by(*group_by_fields)

    # Aplicar filtros
    filtros = []

    if codigo:
        filtros.append(Venta.VENDOC.like(f'%{codigo}%'))

    if sucursal:
        filtros.append(Venta.SUCCOD == sucursal)

    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            filtros.append(Venta.VENFEC >= fecha_inicio_obj)
        except ValueError:
            pass

    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            filtros.append(Venta.VENFEC <= fecha_fin_obj)
        except ValueError:
            pass

    # Aplicar filtros a la consulta
    if filtros:
        query = query.filter(and_(*filtros))

    # Ordenar por fecha de venta descendente
    query = query.order_by(Venta.VENFEC.desc(), Venta.VENDOC.desc())

    # Debug SQL
    from sqlalchemy.dialects import mysql
    sql_compilado = str(query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    print(f"[DEBUG VENTAS SQL] Query generado:")
    print(sql_compilado)

    # Ejecutar consulta
    try:
        resultados = query.all()
        print(f"[DEBUG VENTAS] Query ejecutado exitosamente. Resultados: {len(resultados)}")
    except Exception as e:
        print(f"[ERROR VENTAS] Error al ejecutar query: {str(e)}")
        raise

    # Formatear resultados según el modo
    items = []

    if detalle_productos:
        # Modo DETALLE: Una fila por producto
        for row in resultados:
            items.append({
                'codigoProducto': row.codigo_producto or '',
                'nombreProducto': row.nombre_producto or 'N/A',
                'numeroVentas': int(row.numero_ventas) if row.numero_ventas else 0,
                'cantidadTotal': float(row.cantidad_total) if row.cantidad_total else 0,
                'precioPromedio': float(row.precio_promedio) if row.precio_promedio else 0,
                'valorTotal': float(row.valor_total) if row.valor_total else 0,
                'descuento': float(row.descuento) if row.descuento else 0,
                'impuesto': float(row.impuesto) if row.impuesto else 0
            })

        # Estadísticas para modo detalle
        total_transacciones = sum(item['numeroVentas'] for item in items)
        total_valor_ventas = sum(item['valorTotal'] for item in items)
        total_cantidad_vendida = sum(item['cantidadTotal'] for item in items)
        total_productos = len(items)
    else:
        # Modo CABECERA: Una fila por venta
        for row in resultados:
            # Formatear texto de productos (ej: "3 productos" o "1 producto")
            cantidad_prods = int(row.cantidad_productos) if hasattr(row, 'cantidad_productos') and row.cantidad_productos else 0
            texto_productos = f"{cantidad_prods} producto{'s' if cantidad_prods != 1 else ''}"

            item = {
                'codigo': float(row.numero_documento) if row.numero_documento else 0,
                'tipoTransaccion': row.tipo_transaccion or '',
                'fechaVenta': row.fecha_venta.strftime('%Y-%m-%d') if row.fecha_venta else '',
                'horaVenta': row.hora_venta or '',
                'codigoCliente': row.codigo_cliente or '',
                'nombreCliente': row.nombre_cliente or 'N/A',
                'nombreProducto': texto_productos,
                'valorTotal': float(row.valor_total) if row.valor_total else 0,
                'descuento': float(row.descuento) if row.descuento else 0,
                'impuesto': float(row.impuesto) if row.impuesto else 0,
                'estado': row.estado or '',
                'fe': row.fe or '',
                'baseGrabable': float(row.base_grabable) if hasattr(row, 'base_grabable') and row.base_grabable else 0,
                'sucursal': row.sucursal or ''
            }

            # Agregar unidades narradas solo si se solicitó
            if incluir_narradas and hasattr(row, 'unidades_narradas'):
                item['unidadesNarradas'] = row.unidades_narradas or ''

            items.append(item)

        # Calcular estadísticas para modo cabecera
        total_transacciones = len(items)
        total_valor_ventas = sum(item['valorTotal'] for item in items)
        total_productos = 0
        total_cantidad_vendida = 0
        for row in resultados:
            if hasattr(row, 'cantidad_productos'):
                total_productos += int(row.cantidad_productos) if row.cantidad_productos else 0
            if hasattr(row, 'cantidad_total_vendida'):
                total_cantidad_vendida += float(row.cantidad_total_vendida) if row.cantidad_total_vendida else 0

    return {
        'tipo': 'ventas',
        'fecha_generacion': datetime.now().isoformat(),
        'año_consultado': f'20{sufijo_año}',
        'fuente_datos': f'venta{sufijo_año} + dvent{sufijo_año}',
        'filtros_aplicados': {
            'codigo': codigo,
            'sucursal': sucursal,
            'fechaInicio': fecha_inicio,
            'fechaFin': fecha_fin,
            'ubicacion': ubicacion
        },
        'estadisticas': {
            'totalTransacciones': total_transacciones,
            'cantidadTotalProductos': total_productos,
            'cantidadTotalVendida': round(total_cantidad_vendida, 2),
            'valorTotalVentas': round(total_valor_ventas, 2)
        },
        'datos': items
    }


@app.route('/api/detalle_venta/<numero_venta>', methods=['GET'])
def get_detalle_venta(numero_venta):
    """
    Endpoint para obtener el detalle de productos de una venta específica

    Args:
        numero_venta: Número de documento de venta (VENDOC)
    """
    try:
        # Obtener parámetros opcionales
        fecha_inicio = request.args.get('fechaInicio')
        fecha_fin = request.args.get('fechaFin')

        # Determinar año desde los filtros
        from reports import determinar_año_desde_filtros, crear_modelo_dventa

        filtros_dict = {
            'fechaInicio': fecha_inicio,
            'fechaFin': fecha_fin
        }
        sufijo_año = determinar_año_desde_filtros(filtros_dict)

        print(f"[DEBUG DETALLE] Consultando detalle de venta {numero_venta}, año: 20{sufijo_año}")

        # Crear modelo dinámico de Dventa
        Dventa = crear_modelo_dventa(sufijo_año, db)

        # Construir query para obtener detalle de la venta
        query = db.session.query(
            Dventa.DVECOD.label('codigo_producto'),
            Pas.PASNOM.label('nombre_producto'),
            Dventa.DVECAN.label('cantidad'),
            Dventa.DVEPRE.label('precio_unitario'),
            Dventa.DVEVAL.label('valor_linea'),
            Dventa.DVEDESCUEN.label('descuento_linea'),
            Dventa.DVEIMP.label('impuesto_linea'),
            Dventa.TRNTIPO.label('tipo_transaccion')
        ).outerjoin(
            Pas, Dventa.DVECOD == Pas.PAS
        ).filter(
            Dventa.DVENUM == float(numero_venta)
        ).order_by(Dventa.DVECOD)

        # Debug SQL
        from sqlalchemy.dialects import mysql
        sql_compilado = str(query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
        print(f"[DEBUG DETALLE SQL] Query generado:")
        print(sql_compilado)

        # Ejecutar consulta
        resultados = query.all()
        print(f"[DEBUG DETALLE] Productos encontrados: {len(resultados)}")

        # Formatear resultados
        items = []
        total_valor = 0

        for row in resultados:
            valor_linea = float(row.valor_linea) if row.valor_linea else 0
            total_valor += valor_linea

            items.append({
                'codigoProducto': row.codigo_producto or '',
                'nombreProducto': row.nombre_producto or 'N/A',
                'cantidad': float(row.cantidad) if row.cantidad else 0,
                'precioUnitario': float(row.precio_unitario) if row.precio_unitario else 0,
                'valorLinea': valor_linea,
                'descuentoLinea': float(row.descuento_linea) if row.descuento_linea else 0,
                'impuestoLinea': float(row.impuesto_linea) if row.impuesto_linea else 0,
                'tipoTransaccion': row.tipo_transaccion or ''
            })

        return jsonify({
            'tipo': 'detalle_venta',
            'numero_venta': numero_venta,
            'año_consultado': f'20{sufijo_año}',
            'total_productos': len(items),
            'valor_total': round(total_valor, 2),
            'productos': items
        })

    except Exception as e:
        print(f"[ERROR DETALLE] Error al obtener detalle de venta: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/reportes/productos-vendidos', methods=['GET'])
def get_productos_vendidos():
    """
    Endpoint para el 2do Informe: Productos Vendidos
    """
    try:
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'grupo': request.args.get('grupo'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin')
        }

        resultado = reporte_productos_vendidos(db, Pas, Artic, filtros)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el reporte de productos vendidos',
            'detalle': str(e)
        }), 500


@app.route('/api/reportes/utilidad', methods=['GET'])
def get_utilidad():
    """
    Endpoint para el 3er Informe: Utilidad/Ganancias
    """
    try:
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'grupo': request.args.get('grupo'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin')
        }

        resultado = reporte_utilidad(db, Pas, Artic, filtros)
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'error': 'Error al procesar el reporte de utilidad',
            'detalle': str(e)
        }), 500


@app.route('/api/exportar', methods=['GET'])
def exportar_reporte():
    """
    Endpoint para exportar reportes a Excel o PDF

    Parámetros:
    - tipo: tipo de reporte (inventario, ventas, productos-vendidos, utilidad)
    - formato: formato de exportación (excel, pdf)
    - Todos los filtros del reporte correspondiente
    """
    try:
        tipo_reporte = request.args.get('tipo', 'inventario')
        formato = request.args.get('formato', 'excel')

        # Obtener filtros
        filtros = {
            'codigo': request.args.get('codigo'),
            'sucursal': request.args.get('sucursal'),
            'proveedor': request.args.get('proveedor'),
            'grupo': request.args.get('grupo'),
            'fechaInicio': request.args.get('fechaInicio'),
            'fechaFin': request.args.get('fechaFin'),
            'estado': request.args.get('estado'),
            'ubicacion': request.args.get('ubicacion')
        }

        # Generar el reporte según el tipo
        if tipo_reporte == 'inventario':
            datos = reporte_inventario(
                codigo=filtros.get('codigo'),
                sucursal=filtros.get('sucursal'),
                proveedor=filtros.get('proveedor'),
                fecha_inicio=filtros.get('fechaInicio'),
                fecha_fin=filtros.get('fechaFin'),
                estado=filtros.get('estado'),
                ubicacion=filtros.get('ubicacion')
            )
        elif tipo_reporte == 'ventas':
            # Obtener opciones de exportación
            incluir_narradas = request.args.get('incluir_narradas', 'false').lower() == 'true'
            detalle_productos = request.args.get('detalle_productos', 'false').lower() == 'true'

            datos = reporte_ventas(
                codigo=filtros.get('codigo'),
                sucursal=filtros.get('sucursal'),
                fecha_inicio=filtros.get('fechaInicio'),
                fecha_fin=filtros.get('fechaFin'),
                ubicacion=filtros.get('ubicacion'),
                incluir_narradas=incluir_narradas,
                detalle_productos=detalle_productos
            )
        elif tipo_reporte == 'productos-vendidos':
            datos = reporte_productos_vendidos(db, Pas, Artic, filtros)
        elif tipo_reporte == 'utilidad':
            datos = reporte_utilidad(db, Pas, Artic, filtros)
        else:
            return jsonify({
                'error': f'Tipo de reporte no soportado: {tipo_reporte}'
            }), 400

        # Exportar según el formato
        if formato == 'excel':
            buffer = exportar_a_excel(datos, tipo_reporte)
            filename = f'reporte_{tipo_reporte}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

            return send_file(
                buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        elif formato == 'pdf':
            buffer = exportar_a_pdf(datos, tipo_reporte)
            filename = f'reporte_{tipo_reporte}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({
                'error': f'Formato no soportado: {formato}'
            }), 400

    except Exception as e:
        return jsonify({
            'error': 'Error al exportar el reporte',
            'detalle': str(e)
        }), 500


# ========================================
# PUNTO DE ENTRADA
# ========================================

if __name__ == '__main__':
    # Configuración del servidor
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

    print(f"""
    ============================================================
      Servidor Flask - Sistema de Reportes
    ============================================================
      Puerto: {port}
      Debug: {debug}
      Base de datos: MySQL (SQLAlchemy)
    ============================================================

    Endpoints disponibles:
    - GET  /api/health                      -> Verificacion de estado
    - GET  /api/reportes                    -> Reportes (inventario, ventas)
    - GET  /api/reportes/productos-vendidos -> 2do Informe: Productos Vendidos
    - GET  /api/reportes/utilidad           -> 3er Informe: Utilidad/Ganancias
    - GET  /api/exportar                    -> Exportar a Excel/PDF

    Ejemplos de uso:
    http://localhost:{port}/api/reportes?tipo=inventario&sucursal=01
    http://localhost:{port}/api/reportes/productos-vendidos?fechaInicio=2025-01-01&fechaFin=2025-12-31
    http://localhost:{port}/api/reportes/utilidad?sucursal=01&fechaInicio=2025-01-01
    http://localhost:{port}/api/exportar?tipo=utilidad&formato=excel&fechaInicio=2025-01-01
    """)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
