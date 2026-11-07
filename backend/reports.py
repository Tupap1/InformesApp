"""
Módulo de Reportes con Modelos Dinámicos
Maneja la generación de reportes de inventario, ventas y utilidad con formato mejorado
"""

from sqlalchemy import Column, String, Float, Date, Boolean, Text, Integer, func, and_
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape, legal
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers

Base = declarative_base()


# ========================================
# FUNCIONES AUXILIARES
# ========================================

def formatear_numero(numero):
    """
    Formatea números grandes con sufijos K (miles) o M (millones)

    Args:
        numero (float): Número a formatear

    Returns:
        str o float: Número formateado con sufijo si es muy grande
    """
    if numero is None:
        return 0

    numero = float(numero)

    # Si es menor a 10,000, retornar sin formato
    if abs(numero) < 10000:
        return round(numero, 2)

    # Si es mayor a 1 millón, usar M
    if abs(numero) >= 1000000:
        return f"{round(numero / 1000000, 2)}M"

    # Si es mayor a 10,000, usar K
    if abs(numero) >= 10000:
        return f"{round(numero / 1000, 2)}K"

    return round(numero, 2)


def determinar_año_desde_filtros(filtros):
    """
    Extrae el año de los filtros para determinar el sufijo de las tablas anuales

    Args:
        filtros (dict): Diccionario con fechaInicio, fechaFin, etc.

    Returns:
        str: Sufijo del año (ej: '25' para 2025)
    """
    # Intentar obtener el año de fechaFin primero
    if filtros.get('fechaFin'):
        try:
            fecha = datetime.strptime(filtros['fechaFin'], '%Y-%m-%d')
            return fecha.strftime('%y')  # Retorna últimos 2 dígitos (ej: '25')
        except:
            pass

    # Si no hay fechaFin, intentar con fechaInicio
    if filtros.get('fechaInicio'):
        try:
            fecha = datetime.strptime(filtros['fechaInicio'], '%Y-%m-%d')
            return fecha.strftime('%y')
        except:
            pass

    # Por defecto, año actual
    return datetime.now().strftime('%y')


def aplicar_formato_excel(worksheet, df, tiene_totales=False):
    """
    Aplica formato profesional a una hoja de Excel

    Args:
        worksheet: Hoja de trabajo de openpyxl
        df: DataFrame de pandas con los datos
        tiene_totales (bool): Si la última fila tiene totales
    """
    # Colores
    color_encabezado = 'D3D3D3'  # Gris claro
    color_totales = 'E8E8E8'  # Gris más claro

    # Fuentes
    fuente_encabezado = Font(name='Arial', size=11, bold=True, color='000000')
    fuente_normal = Font(name='Arial', size=10)
    fuente_totales = Font(name='Arial', size=10, bold=True)

    # Bordes
    borde_delgado = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Aplicar formato a encabezados (fila 1)
    for col_num, column_title in enumerate(df.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.font = fuente_encabezado
        cell.fill = PatternFill(start_color=color_encabezado, end_color=color_encabezado, fill_type='solid')
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = borde_delgado

    # Aplicar formato a datos
    num_rows = len(df)
    ultima_fila_datos = num_rows if not tiene_totales else num_rows - 1

    for row_num in range(2, ultima_fila_datos + 2):
        for col_num in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.font = fuente_normal
            cell.border = borde_delgado
            cell.alignment = Alignment(horizontal='left', vertical='center')

            # Identificar columnas monetarias y aplicar formato
            column_name = df.columns[col_num - 1].lower()
            if any(keyword in column_name for keyword in ['precio', 'costo', 'valor', 'ganancia', 'venta', 'total', 'utilidad']):
                # Verificar que no sea un porcentaje
                if 'porcentaje' not in column_name and '%' not in column_name:
                    cell.number_format = '"$"#,##0.00'
                    cell.alignment = Alignment(horizontal='right', vertical='center')
            elif 'cantidad' in column_name or 'existencia' in column_name:
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif 'porcentaje' in column_name or '%' in column_name:
                cell.number_format = '0.00"%"'
                cell.alignment = Alignment(horizontal='right', vertical='center')

    # Aplicar formato a totales si existe
    if tiene_totales:
        fila_totales = num_rows + 1
        for col_num in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=fila_totales, column=col_num)
            cell.font = fuente_totales
            cell.fill = PatternFill(start_color=color_totales, end_color=color_totales, fill_type='solid')
            cell.border = borde_delgado
            cell.alignment = Alignment(horizontal='right', vertical='center')

            # Formato monetario para totales
            column_name = df.columns[col_num - 1].lower()
            if any(keyword in column_name for keyword in ['precio', 'costo', 'valor', 'ganancia', 'venta', 'total', 'utilidad']):
                if 'porcentaje' not in column_name and '%' not in column_name:
                    cell.number_format = '"$"#,##0.00'

    # Ajustar ancho de columnas
    for col_num, column_title in enumerate(df.columns, 1):
        column_letter = worksheet.cell(row=1, column=col_num).column_letter

        # Calcular ancho basado en el título y contenido
        max_length = len(str(column_title))
        for row_num in range(2, min(num_rows + 2, 102)):  # Revisar hasta 100 filas
            cell_value = str(worksheet.cell(row=row_num, column=col_num).value or '')
            max_length = max(max_length, len(cell_value))

        # Establecer ancho (con límite máximo de 50)
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column_letter].width = adjusted_width


# ========================================
# FUNCIÓN: Crear Modelos Dinámicos
# ========================================

def crear_modelo_venta(sufijo_año, db):
    """
    Crea el modelo dinámico para la tabla VENTA del año especificado

    Args:
        sufijo_año (str): Sufijo del año (ej: '25')
        db: Instancia de SQLAlchemy

    Returns:
        class: Clase del modelo Venta
    """
    nombre_tabla = f'venta{sufijo_año}'

    class Venta(db.Model):
        __tablename__ = nombre_tabla
        __table_args__ = {'extend_existing': True}

        # Campos clave (primary key)
        VENDOC = Column(String(20), primary_key=True)
        TRNTIPO = Column(String(3), primary_key=True)

        # Campos de información de venta
        SUCCOD = Column(String(10), nullable=False)
        VENFEC = Column(Date)
        VENHOR = Column(String(8))
        VENCLI = Column(String(20))
        VENNOM = Column(String(100))
        VENVAL = Column(Float, default=0)
        VENDES = Column(Float, default=0)
        VENIMP = Column(Float, default=0)
        VENEST = Column(String(3))
        VENNAR = Column(Float, default=0)  # Unidades narradas
        FACELECESTA = Column(String(10))  # Estado factura electrónica
        CLIIDENTIFI = Column(String(20))

        def __repr__(self):
            return f'<Venta {self.VENDOC}>'

    return Venta


def crear_modelo_dventa(sufijo_año, db):
    """
    Crea el modelo dinámico para la tabla DVENT (Detalle de venta) del año especificado

    Args:
        sufijo_año (str): Sufijo del año (ej: '25')
        db: Instancia de SQLAlchemy

    Returns:
        class: Clase del modelo Dventa
    """
    nombre_tabla = f'dvent{sufijo_año}'

    class Dventa(db.Model):
        __tablename__ = nombre_tabla
        __table_args__ = {'extend_existing': True}

        # Campos clave (primary key)
        DVENUM = Column(String(20), primary_key=True)  # Número de documento
        TRNTIPO = Column(String(3), primary_key=True)  # Tipo de transacción
        DVELIN = Column(Integer, primary_key=True)     # Línea del detalle

        # Campos de detalle del producto
        DVECOD = Column(String(50), nullable=False)    # Código del producto
        DVECAN = Column(Float, nullable=False, default=0)  # Cantidad
        DVEPRE = Column(Float, nullable=False, default=0)  # Precio unitario
        DVEVAL = Column(Float, nullable=False, default=0)  # Valor total línea
        DVEDESCUEN = Column(Float, default=0)  # Descuento línea
        DVEIMP = Column(Float, default=0)  # Impuesto línea
        PASCOS = Column(Float)  # Costo del producto
        SUCCOD = Column(String(10))  # Sucursal

        def __repr__(self):
            return f'<Dventa {self.DVENUM}-{self.DVELIN}>'

    return Dventa


# ========================================
# FUNCIONES DE REPORTES
# ========================================

def reporte_productos_vendidos(db, Pas, Artic, filtros):
    """
    2do Informe: Productos Vendidos

    Genera reporte de productos vendidos usando las tablas VENTA y DVENT
    Agrupa por producto (DVECOD) sumando todas las ventas
    Incluye ARTCPR y ARTCOS de la tabla Artic

    Args:
        db: Instancia de SQLAlchemy
        Pas: Modelo de la tabla pas (NO USADO - tabla no existe en BD local)
        Artic: Modelo de la tabla artic
        filtros (dict): Filtros de búsqueda

    Returns:
        dict: Resultado del reporte
    """
    # Determinar año desde los filtros
    sufijo_año = determinar_año_desde_filtros(filtros)

    print(f"[DEBUG PRODUCTOS VENDIDOS] Usando año: 20{sufijo_año}, tablas: venta{sufijo_año}, dvent{sufijo_año}")

    # Crear modelos dinámicos
    Venta = crear_modelo_venta(sufijo_año, db)
    Dventa = crear_modelo_dventa(sufijo_año, db)

    # Construir query: Agrupar por producto desde DVENT
    # Removido JOIN con Pas (no existe en BD local)
    query = db.session.query(
        Dventa.DVECOD.label('codigo'),
        func.coalesce(Artic.ARTNOM, Dventa.DVECOD).label('descripcion'),  # Usar ARTNOM en lugar de PASNOM
        func.sum(Dventa.DVECAN).label('cuantos_se_vendio'),
        func.avg(Dventa.DVEPRE).label('precio_promedio'),
        func.sum(Dventa.DVEVAL).label('valor_total_vendido'),
        func.coalesce(Artic.ARTEXI, 0).label('existencias'),
        func.coalesce(Artic.ARTCPR, 0).label('costo_promedio'),
        func.coalesce(Artic.ARTCOS, 0).label('costo_articulo'),
        func.coalesce(Artic.PROCODIGO, '').label('proveedor')
    ).join(
        Venta, and_(
            Dventa.DVENUM == Venta.VENDOC,
            Dventa.TRNTIPO == Venta.TRNTIPO
        )
    ).outerjoin(
        Artic, Dventa.DVECOD == Artic.ARTCOD
    )

    # Aplicar filtros
    filtros_lista = []

    if filtros.get('codigo'):
        filtros_lista.append(Dventa.DVECOD.like(f"%{filtros['codigo']}%"))

    if filtros.get('sucursal'):
        filtros_lista.append(Venta.SUCCOD == filtros['sucursal'])

    if filtros.get('fechaInicio'):
        try:
            fecha_inicio = datetime.strptime(filtros['fechaInicio'], '%Y-%m-%d').date()
            filtros_lista.append(Venta.VENFEC >= fecha_inicio)
        except:
            pass

    if filtros.get('fechaFin'):
        try:
            fecha_fin = datetime.strptime(filtros['fechaFin'], '%Y-%m-%d').date()
            filtros_lista.append(Venta.VENFEC <= fecha_fin)
        except:
            pass

    if filtros.get('proveedor'):
        filtros_lista.append(Artic.PROCODIGO == filtros['proveedor'])

    # Removido filtro de grupo (Pas.GRUPCODI no existe)

    # Aplicar filtros a la query
    if filtros_lista:
        query = query.filter(and_(*filtros_lista))

    # Agrupar por producto
    query = query.group_by(Dventa.DVECOD)

    # Ordenar por valor total vendido (descendente) - DE MAYOR A MENOR
    query = query.order_by(func.sum(Dventa.DVEVAL).desc())

    # Ejecutar query
    try:
        resultados = query.all()
        print(f"[DEBUG] Query ejecutado exitosamente. Resultados: {len(resultados)}")
    except Exception as e:
        print(f"[ERROR] Error al ejecutar query: {str(e)}")
        raise

    # Formatear resultados
    items = []
    total_vendido = 0
    total_valor = 0

    for idx, row in enumerate(resultados):
        if idx < 3:  # Debug: mostrar primeras 3 filas
            print(f"[DEBUG] Row {idx}: codigo={row.codigo}, desc={row.descripcion}, cant={row.cuantos_se_vendio}, precio={row.precio_promedio}")

        cantidad_vendida = float(row.cuantos_se_vendido) if row.cuantos_se_vendio else 0
        valor_total = float(row.valor_total_vendido) if row.valor_total_vendido else 0

        total_vendido += cantidad_vendida
        total_valor += valor_total

        items.append({
            'codigo': str(row.codigo) if row.codigo else '',
            'descripcion': str(row.descripcion) if row.descripcion else 'N/A',
            'cuantos_se_vendio': round(cantidad_vendida, 2),
            'precio_promedio': round(float(row.precio_promedio), 2) if row.precio_promedio else 0,
            'valor_total_vendido': round(valor_total, 2),
            'existencias': float(row.existencias) if row.existencias else 0,
            'costo_promedio': round(float(row.costo_promedio), 2) if row.costo_promedio else 0,
            'costo_articulo': round(float(row.costo_articulo), 2) if row.costo_articulo else 0,
            'proveedor': str(row.proveedor) if row.proveedor else ''
        })

    return {
        'tipo': 'productos_vendidos',
        'fecha_generacion': datetime.now().isoformat(),
        'fuente_datos': f'venta{sufijo_año} + dvent{sufijo_año}',
        'filtros_aplicados': filtros,
        'estadisticas': {
            'totalProductos': len(items),
            'totalCantidadVendida': formatear_numero(total_vendido),
            'totalValorVendido': formatear_numero(total_valor)
        },
        'datos': items
    }


def reporte_utilidad(db, Pas, Artic, filtros):
    """
    3er Informe: Utilidad/Ganancias

    Genera reporte de utilidad con ganancias en pesos y porcentaje
    Ordenado por margen % (descendente) y luego por ganancia absoluta (descendente)
    Incluye ARTCPR y ARTCOS de la tabla Artic

    Args:
        db: Instancia de SQLAlchemy
        Pas: Modelo de la tabla pas (NO USADO - tabla no existe en BD local)
        Artic: Modelo de la tabla artic
        filtros (dict): Filtros de búsqueda

    Returns:
        dict: Resultado del reporte
    """
    # Determinar año y crear modelos dinámicos
    sufijo_año = determinar_año_desde_filtros(filtros)
    print(f"[DEBUG UTILIDAD] Usando año: 20{sufijo_año}, tablas: venta{sufijo_año}, dvent{sufijo_año}")
    Venta = crear_modelo_venta(sufijo_año, db)
    Dventa = crear_modelo_dventa(sufijo_año, db)

    # Construir query con cálculos de utilidad
    # Removido JOIN con Pas (no existe en BD local)
    query = db.session.query(
        Dventa.DVECOD.label('codigo'),
        func.coalesce(Artic.ARTNOM, Dventa.DVECOD).label('descripcion'),  # Usar ARTNOM en lugar de PASNOM
        func.sum(Dventa.DVECAN).label('cuantos_se_vendio'),
        func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0).label('costo_promedio'),  # Costo promedio
        func.coalesce(Artic.ARTCOS, 0).label('costo_articulo'),
        func.avg(Dventa.DVEPRE).label('precio_de_venta'),
        (func.sum(Dventa.DVEPRE * Dventa.DVECAN) -
         func.sum(func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0) * Dventa.DVECAN)).label('ganancia_en_pesos'),
        func.sum(Dventa.DVEPRE * Dventa.DVECAN).label('total_ventas')
    ).outerjoin(
        Artic, and_(
            Dventa.DVECOD == Artic.ARTCOD,
            Dventa.SUCCOD == Artic.SUCCOD
        )
    ).join(
        Venta, and_(
            Dventa.DVENUM == Venta.VENDOC,
            Dventa.TRNTIPO == Venta.TRNTIPO
        )
    )

    # Aplicar filtros (misma lógica que productos vendidos)
    filtros_lista = []

    if filtros.get('codigo'):
        filtros_lista.append(Dventa.DVECOD.like(f"%{filtros['codigo']}%"))

    if filtros.get('sucursal'):
        filtros_lista.append(Dventa.SUCCOD == filtros['sucursal'])

    if filtros.get('fechaInicio'):
        try:
            fecha_inicio = datetime.strptime(filtros['fechaInicio'], '%Y-%m-%d').date()
            filtros_lista.append(Venta.VENFEC >= fecha_inicio)
        except:
            pass

    if filtros.get('fechaFin'):
        try:
            fecha_fin = datetime.strptime(filtros['fechaFin'], '%Y-%m-%d').date()
            filtros_lista.append(Venta.VENFEC <= fecha_fin)
        except:
            pass

    if filtros.get('proveedor'):
        filtros_lista.append(Artic.PROCODIGO == filtros['proveedor'])

    # Removido filtro de grupo (Pas.GRUPCODI no existe)

    if filtros_lista:
        query = query.filter(and_(*filtros_lista))

    # Agrupar por producto
    query = query.group_by(
        Dventa.DVECOD,
        func.coalesce(Artic.ARTNOM, Dventa.DVECOD),
        func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0),
        func.coalesce(Artic.ARTCOS, 0)
    )

    # NO ordenamos aquí - lo haremos después de calcular el margen %

    # Ejecutar query
    try:
        resultados = query.all()
        print(f"[DEBUG UTILIDAD] Query ejecutado exitosamente. Resultados: {len(resultados)}")
    except Exception as e:
        print(f"[ERROR UTILIDAD] Error al ejecutar query: {str(e)}")
        raise

    # Formatear resultados y calcular margen %
    items = []
    total_ganancia_pesos = 0
    total_ventas = 0

    for idx, row in enumerate(resultados):
        ganancia_pesos = float(row.ganancia_en_pesos) if row.ganancia_en_pesos else 0
        ventas = float(row.total_ventas) if row.total_ventas else 0

        # Calcular porcentaje de ganancia (margen %)
        if ventas > 0:
            ganancia_porcentaje = (ganancia_pesos / ventas) * 100
        else:
            ganancia_porcentaje = 0

        total_ganancia_pesos += ganancia_pesos
        total_ventas += ventas

        items.append({
            'codigo': str(row.codigo) if row.codigo else '',
            'descripcion': str(row.descripcion) if row.descripcion else 'N/A',
            'cuantos_se_vendio': float(row.cuantos_se_vendio) if row.cuantos_se_vendio else 0,
            'costo_promedio': float(row.costo_promedio) if row.costo_promedio else 0,
            'costo_articulo': float(row.costo_articulo) if row.costo_articulo else 0,
            'precio_de_venta': float(row.precio_de_venta) if row.precio_de_venta else 0,
            'ganancia_en_pesos': round(ganancia_pesos, 2),
            'ganancias_en_porcentaje': round(ganancia_porcentaje, 2),
            'total_ventas': round(ventas, 2)
        })

    # ORDENAR: Primero por margen % (desc), luego por ganancia absoluta (desc)
    items.sort(key=lambda x: (x['ganancias_en_porcentaje'], x['ganancia_en_pesos']), reverse=True)

    # Calcular porcentaje total
    if total_ventas > 0:
        porcentaje_total = (total_ganancia_pesos / total_ventas) * 100
    else:
        porcentaje_total = 0

    return {
        'tipo': 'utilidad',
        'fecha_generacion': datetime.now().isoformat(),
        'año_consultado': f'20{sufijo_año}',
        'filtros_aplicados': filtros,
        'estadisticas': {
            'totalProductos': len(items),
            'totalVentas': formatear_numero(total_ventas),
            'totalGananciaPesos': formatear_numero(total_ganancia_pesos),
            'porcentajeGananciaTotal': f"{round(porcentaje_total, 2)}%"
        },
        'datos': items
    }


# ========================================
# FUNCIONES DE EXPORTACIÓN
# ========================================

def exportar_excel(data, tipo_reporte):
    """
    Exporta datos a Excel con formato profesional
    Orden: Detallado → Totales

    Args:
        data (dict): Datos del reporte
        tipo_reporte (str): Tipo de reporte ('productos_vendidos', 'utilidad', etc.)

    Returns:
        BytesIO: Archivo Excel en memoria
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # HOJA 1: DETALLADO (primero)
        df_detallado = pd.DataFrame(data['datos'])

        # Renombrar columnas para que sean más legibles
        column_map = {
            'codigo': 'Código',
            'descripcion': 'Descripción',
            'cuantos_se_vendio': 'Cantidad Vendida',
            'precio_promedio': 'Precio Promedio',
            'precio_de_venta': 'Precio de Venta',
            'valor_total_vendido': 'Valor Total Vendido',
            'existencias': 'Existencias',
            'costo_promedio': 'Costo Promedio',
            'costo_articulo': 'Costo Artículo',
            'marca': 'Marca',
            'proveedor': 'Proveedor',
            'ganancia_en_pesos': 'Ganancia ($)',
            'ganancias_en_porcentaje': 'Margen (%)',
            'total_ventas': 'Total Ventas',
            'costo': 'Costo'
        }

        df_detallado.rename(columns=column_map, inplace=True)

        # Agregar fila de totales si aplica
        tiene_totales = False
        if tipo_reporte in ['productos_vendidos', 'utilidad']:
            tiene_totales = True
            totales = {}

            for col in df_detallado.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['cantidad', 'vendida', 'valor', 'total', 'ganancia', 'venta', 'existencia']):
                    if 'porcentaje' not in col_lower and '%' not in col_lower:
                        totales[col] = df_detallado[col].sum() if col in df_detallado.select_dtypes(include=['number']).columns else ''
                    else:
                        totales[col] = ''
                else:
                    totales[col] = 'TOTALES' if col == df_detallado.columns[0] else ''

            # Agregar fila de totales
            df_detallado = pd.concat([df_detallado, pd.DataFrame([totales])], ignore_index=True)

        # Escribir a Excel
        df_detallado.to_excel(writer, sheet_name='Detallado', index=False)

        # Aplicar formato
        worksheet = writer.sheets['Detallado']
        aplicar_formato_excel(worksheet, df_detallado, tiene_totales=tiene_totales)

        # HOJA 2: TOTALES (segundo)
        if 'estadisticas' in data:
            df_totales = pd.DataFrame([data['estadisticas']]).T
            df_totales.columns = ['Valor']
            df_totales.reset_index(inplace=True)
            df_totales.rename(columns={'index': 'Métrica'}, inplace=True)

            df_totales.to_excel(writer, sheet_name='Totales', index=False)

            # Aplicar formato a totales
            worksheet_totales = writer.sheets['Totales']
            aplicar_formato_excel(worksheet_totales, df_totales, tiene_totales=False)

    output.seek(0)
    return output


def exportar_pdf(data, tipo_reporte):
    """
    Exporta datos a PDF con formato horizontal (Legal Landscape)
    Evita sobreposición de datos y usa todo el espacio disponible

    Args:
        data (dict): Datos del reporte
        tipo_reporte (str): Tipo de reporte

    Returns:
        BytesIO: Archivo PDF en memoria
    """
    output = BytesIO()

    # Usar Legal Landscape (14" x 8.5") para más espacio horizontal
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(legal),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.5*inch
    )

    elements = []
    styles = getSampleStyleSheet()

    # Estilo para encabezado
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Estilo para subtítulo
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    def crear_encabezado_tabla():
        """Crea el encabezado que se repite en cada página"""
        fecha_gen = datetime.fromisoformat(data['fecha_generacion']).strftime('%d/%m/%Y %H:%M')

        # Título
        titulo_map = {
            'productos_vendidos': 'Reporte de Productos Vendidos',
            'utilidad': 'Reporte de Utilidad y Ganancias'
        }
        titulo = Paragraph(titulo_map.get(tipo_reporte, 'Reporte'), title_style)
        elements.append(titulo)

        # Subtítulo con fecha
        subtitulo = Paragraph(f'Generado el {fecha_gen}', subtitle_style)
        elements.append(subtitulo)

    # Agregar encabezado inicial
    crear_encabezado_tabla()

    # Preparar datos para la tabla
    df = pd.DataFrame(data['datos'])

    # Limitar columnas para que quepan en horizontal
    if tipo_reporte == 'productos_vendidos':
        columnas_mostrar = ['codigo', 'descripcion', 'cuantos_se_vendio', 'precio_promedio',
                          'valor_total_vendido', 'costo_promedio', 'costo_articulo']
        headers = ['Código', 'Descripción', 'Cant.', 'Precio Prom.', 'Valor Total', 'Costo Prom.', 'Costo Art.']
    elif tipo_reporte == 'utilidad':
        columnas_mostrar = ['codigo', 'descripcion', 'cuantos_se_vendio', 'precio_de_venta',
                          'costo_promedio', 'costo_articulo', 'ganancia_en_pesos', 'ganancias_en_porcentaje']
        headers = ['Código', 'Descripción', 'Cant.', 'Precio Venta', 'Costo Prom.', 'Costo Art.', 'Ganancia ($)', 'Margen (%)']
    else:
        columnas_mostrar = df.columns.tolist()[:7]  # Primeras 7 columnas
        headers = columnas_mostrar

    # Filtrar columnas
    df_filtrado = df[columnas_mostrar]

    # Crear tabla
    table_data = [headers]

    for _, row in df_filtrado.iterrows():
        fila = []
        for col in columnas_mostrar:
            valor = row[col]
            # Truncar texto largo
            if isinstance(valor, str) and len(valor) > 30:
                valor = valor[:27] + '...'
            elif isinstance(valor, (int, float)):
                valor = f'{valor:,.2f}'
            fila.append(str(valor))
        table_data.append(fila)

    # Calcular anchos de columna dinámicamente
    page_width = landscape(legal)[0] - 1*inch  # Restar márgenes
    num_cols = len(headers)
    col_width = page_width / num_cols
    col_widths = [col_width] * num_cols

    # Crear tabla con anchos calculados
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Estilo de tabla
    table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Primeras 2 columnas alineadas a la izquierda
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Resto alineadas a la derecha
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#2C3E50')),

        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
    ]))

    elements.append(table)

    # Agregar estadísticas al final
    if 'estadisticas' in data:
        elements.append(Spacer(1, 0.3*inch))
        stats_data = [[k.replace('_', ' ').title(), str(v)] for k, v in data['estadisticas'].items()]
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)

    # Construir PDF
    doc.build(elements)

    output.seek(0)
    return output
