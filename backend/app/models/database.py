"""
Modelos de Base de Datos - Artic, Articv, Pas, Proveedo
"""

from app import db
from datetime import datetime
from sqlalchemy import Column, String, Float, Date, Boolean, Text, Integer


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

    # Clave primaria compuesta
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
    PASOBSERVA = db.Column(db.Text, nullable=False)  # Descripción del producto
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
