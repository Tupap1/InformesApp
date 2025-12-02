"""
Módulo de Reportes con Modelos Dinámicos
Maneja la generación de reportes de inventario, ventas y utilidad
"""

from sqlalchemy import Column, String, Float, Date, Boolean, Text, Integer, func, and_
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
        __table_args__ = {'extend_existing': True}  # Removido schema para usar DB por defecto

        # Clave primaria compuesta
        VENDOC = Column(Float, primary_key=True, nullable=False, default=0)
        TRNTIPO = Column(String(5), primary_key=True, nullable=False, default='')

        # Campos principales
        VENCIA = Column(String(1), nullable=False, default='')
        VENCLI = Column(String(15), nullable=False, default='')  # Cliente
        VENNOM = Column(String(40), nullable=False, default='')  # Nombre cliente
        VENVEN = Column(String(5), nullable=False, default='')   # Vendedor
        VENVAL = Column(Float, nullable=False, default=0)        # Valor total
        VENDES = Column(Float, nullable=False, default=0)        # Descuento
        VENIMP = Column(Float, nullable=False, default=0)        # Impuesto
        VENCOM = Column(Float, nullable=False, default=0)
        VENNAR = Column(Float, nullable=False, default=0)
        VENFEC = Column(Date, nullable=False, default=datetime(2000, 1, 1))  # Fecha venta
        VENHOR = Column(String(8), nullable=False, default='')   # Hora
        VENEST = Column(String(1), nullable=False, default='')   # Estado
        VENCAM = Column(Float, nullable=False, default=0)
        VENGRAVADO = Column(Float, nullable=False, default=0)
        VENEXENTO = Column(Float, nullable=False, default=0)
        SUCCOD = Column(String(2), nullable=False, default='')   # Sucursal
        PRFACTCONV = Column(Float, nullable=False, default=0)
        VENCIERRE = Column(Date, nullable=False, default=datetime(2000, 1, 1))
        VENOBSERVA = Column(String(200), nullable=False, default='')
        FACFACPOS = Column(Float, nullable=False, default=0)
        FACTER = Column(String(80), nullable=False, default='')
        FACTRNORI = Column(String(5), nullable=False, default='')
        FACDOCORI = Column(Float, nullable=False, default=0)
        FACBAT = Column(String(1), nullable=False, default='')
        FACELECESTA = Column(String(1), nullable=False, default='P')
        FACELECMNS = Column(Text, nullable=False)
        CUFE = Column(Text, nullable=False)
        devostat = Column(String(1), nullable=False, default='')
        facidele = Column(Text, nullable=False)
        expedition = Column(Date)
        pdfstatus = Column(Boolean, nullable=False, default=False)

    return Venta


def crear_modelo_dventa(sufijo_año, db):
    """
    Crea el modelo dinámico para la tabla DVENT (Detalle de Venta) del año especificado

    Args:
        sufijo_año (str): Sufijo del año (ej: '25')
        db: Instancia de SQLAlchemy

    Returns:
        class: Clase del modelo Dventa
    """
    nombre_tabla = f'dvent{sufijo_año}'

    class Dventa(db.Model):
        __tablename__ = nombre_tabla
        __table_args__ = {'extend_existing': True}  # Removido schema para usar DB por defecto

        # Clave primaria compuesta
        DVENUM = Column(Float, primary_key=True, nullable=False, default=0)
        DVECOD = Column(String(15), primary_key=True, nullable=False, default='')  # Código producto
        SUCCOD = Column(String(2), primary_key=True, nullable=False, default='')
        TRNTIPO = Column(String(5), primary_key=True, nullable=False, default='')
        DVEID = Column(String(10), primary_key=True, nullable=False, default='')

        # Campos principales
        DVEFEC = Column(Date, nullable=False, default=datetime(2000, 1, 1))
        DVEVAL = Column(Float, nullable=False, default=0)          # Valor
        DVECAN = Column(Float, nullable=False, default=0)          # Cantidad vendida
        DVEDEP = Column(String(20), nullable=False, default='')
        DVEPRE = Column(Float, nullable=False, default=0)          # Precio de venta
        DVEIMP = Column(Float, nullable=False, default=0)          # Impuesto
        DVEFECHAS = Column(String(100), nullable=False, default='')
        DVEDESCUEN = Column(Float, nullable=False, default=0)      # Descuento
        DVEPORIMP = Column(Float, nullable=False, default=0)
        DVEIMP1 = Column(Float, nullable=False, default=0)
        DVEPORIMP1 = Column(Float, nullable=False, default=0)
        DVEOBSERVA = Column(String(250), nullable=False, default='')
        PASCOSPRO = Column(Float, nullable=False, default=0)
        PASCOS = Column(Float, nullable=False, default=0)          # Costo del producto
        UBICODIGO = Column(String(5), nullable=False, default='')
        DVECANDEV = Column(Float, nullable=False, default=0)
        DVELOT = Column(Boolean, nullable=False, default=False)
        DVEFECVEN = Column(Date, nullable=False, default=datetime(2000, 1, 1))
        DVEVEN = Column(String(5), nullable=False, default='')
        DVERETEFNTE = Column(Float, nullable=False, default=0)
        DVERETEIVA = Column(Float, nullable=False, default=0)
        cantunidd = Column(Float, nullable=False, default=0)
        pasimpvaltip = Column(String(1), nullable=False, default='0')
        reteIca = Column(Float, nullable=False, default=0)
        taxpercent2 = Column(Float, nullable=False, default=0)
        taxadv = Column(Float, nullable=False, default=0)

    return Dventa


# ========================================
# FUNCIONES DE REPORTES
# ========================================

def reporte_productos_vendidos(db, Pas, Artic, filtros):
    """
    2do Informe: Productos Vendidos

    Genera reporte de productos vendidos usando las tablas VENTA y DVENT
    Agrupa por producto (DVECOD) sumando todas las ventas

    Args:
        db: Instancia de SQLAlchemy
        Pas: Modelo de la tabla pas
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
    query = db.session.query(
        Dventa.DVECOD.label('codigo'),
        func.coalesce(Pas.PASNOM, Dventa.DVECOD).label('descripcion'),
        func.sum(Dventa.DVECAN).label('cuantos_se_vendio'),
        func.avg(Dventa.DVEPRE).label('precio_promedio'),
        func.sum(Dventa.DVEVAL).label('valor_total_vendido'),
        func.coalesce(Artic.ARTEXI, 0).label('existencias'),
        func.coalesce(Pas.PASMAR, '').label('marca'),
        func.coalesce(Artic.PROCODIGO, '').label('proveedor')
    ).join(
        Venta, and_(
            Dventa.DVENUM == Venta.VENDOC,
            Dventa.TRNTIPO == Venta.TRNTIPO
        )
    ).outerjoin(
        Pas, Dventa.DVECOD == Pas.PAS
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

    if filtros.get('grupo'):
        filtros_lista.append(Pas.GRUPCODI == filtros['grupo'])

    # Aplicar filtros a la query
    if filtros_lista:
        query = query.filter(and_(*filtros_lista))

    # Agrupar por producto
    query = query.group_by(Dventa.DVECOD)

    # Ordenar por cantidad vendida (descendente)
    query = query.order_by(func.sum(Dventa.DVECAN).desc())

    # Debug: Mostrar SQL completo
    from sqlalchemy.dialects import mysql
    sql_compilado = str(query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    print(f"[DEBUG SQL] Query generado (ARTICV):")
    print(sql_compilado)
    print(f"[DEBUG SQL] Parámetros: {query.statement.compile().params}")

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

    for idx, row in enumerate(resultados):
        if idx < 3:  # Debug: mostrar primeras 3 filas
            print(f"[DEBUG] Row {idx}: codigo={row.codigo}, desc={row.descripcion}, cant={row.cuantos_se_vendio}, precio={row.precio_promedio}")

        cantidad_vendida = float(row.cuantos_se_vendio) if row.cuantos_se_vendio else 0
        total_vendido += cantidad_vendida

        items.append({
            'codigo': str(row.codigo) if row.codigo else '',
            'descripcion': str(row.descripcion) if row.descripcion else 'N/A',
            'cuantos_se_vendio': round(cantidad_vendida, 2),
            'precio_promedio': round(float(row.precio_promedio), 2) if row.precio_promedio else 0,
            'valor_total_vendido': round(float(row.valor_total_vendido), 2) if hasattr(row, 'valor_total_vendido') and row.valor_total_vendido else 0,
            'existencias': float(row.existencias) if row.existencias else 0,
            'marca': str(row.marca) if row.marca else '',
            'proveedor': str(row.proveedor) if row.proveedor else ''
        })

    return {
        'tipo': 'productos_vendidos',
        'fecha_generacion': datetime.now().isoformat(),
        'fuente_datos': f'venta{sufijo_año} + dvent{sufijo_año}',
        'filtros_aplicados': filtros,
        'estadisticas': {
            'totalProductos': len(items),
            'totalVendido': formatear_numero(total_vendido)
        },
        'datos': items
    }


def reporte_utilidad(db, Pas, Artic, filtros):
    """
    3er Informe: Utilidad/Ganancias

    Genera reporte de utilidad con ganancias en pesos y porcentaje

    Args:
        db: Instancia de SQLAlchemy
        Pas: Modelo de la tabla pas
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
    # Usar COALESCE para manejar NULLs en el costo
    # Priorizar PASCOS (costo en dvent) sobre ARTCPR (costo promedio en artic)
    from sqlalchemy import func as sqlfunc, case

    query = db.session.query(
        Dventa.DVECOD.label('codigo'),
        Pas.PASNOM.label('descripcion'),
        func.sum(Dventa.DVECAN).label('cuantos_se_vendio'),
        func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0).label('costo'),  # Costo con fallback
        func.avg(Dventa.DVEPRE).label('precio_de_venta'),
        (func.sum(Dventa.DVEPRE * Dventa.DVECAN) -
         func.sum(func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0) * Dventa.DVECAN)).label('ganancia_en_pesos'),
        func.sum(Dventa.DVEPRE * Dventa.DVECAN).label('total_ventas')
    ).join(
        Pas, Dventa.DVECOD == Pas.PAS  # INNER JOIN para garantizar descripción
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

    if filtros.get('grupo'):
        filtros_lista.append(Pas.GRUPCODI == filtros['grupo'])

    if filtros_lista:
        query = query.filter(and_(*filtros_lista))

    # Agrupar por producto
    # Nota: Usando COALESCE en costo, así que lo incluimos en GROUP BY
    query = query.group_by(
        Dventa.DVECOD,
        Pas.PASNOM,
        func.coalesce(Artic.ARTCPR, Dventa.PASCOS, 0)
    )

    # Ordenar por ganancia (descendente)
    query = query.order_by(func.sum(Dventa.DVEPRE * Dventa.DVECAN).desc())

    # Debug: Mostrar SQL completo
    from sqlalchemy.dialects import mysql
    sql_compilado = str(query.statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}))
    print(f"[DEBUG UTILIDAD SQL] Query generado:")
    print(sql_compilado)
    print(f"[DEBUG UTILIDAD SQL] Parámetros: {query.statement.compile().params}")

    # Ejecutar query
    try:
        resultados = query.all()
        print(f"[DEBUG UTILIDAD] Query ejecutado exitosamente. Resultados: {len(resultados)}")
    except Exception as e:
        print(f"[ERROR UTILIDAD] Error al ejecutar query: {str(e)}")
        raise

    # Formatear resultados
    items = []
    total_ganancia_pesos = 0
    total_ventas = 0

    for idx, row in enumerate(resultados):
        if idx < 3:  # Debug: mostrar primeras 3 filas
            print(f"[DEBUG UTILIDAD] Row {idx}: codigo={row.codigo}, desc={row.descripcion}, cant={row.cuantos_se_vendio}, ganancia={row.ganancia_en_pesos}")

        ganancia_pesos = float(row.ganancia_en_pesos) if row.ganancia_en_pesos else 0
        ventas = float(row.total_ventas) if row.total_ventas else 0

        # Calcular porcentaje de ganancia
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
            'costo': float(row.costo) if row.costo else 0,
            'precio_de_venta': float(row.precio_de_venta) if row.precio_de_venta else 0,
            'ganancia_en_pesos': round(ganancia_pesos, 2),
            'ganancias_en_porcentaje': round(ganancia_porcentaje, 2),
            'total_ventas': round(ventas, 2)
        })

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

def exportar_a_excel(datos, tipo_reporte):
    """
    Exporta datos a formato Excel con sumatorias y estadísticas

    Args:
        datos (dict): Datos del reporte
        tipo_reporte (str): Tipo de reporte

    Returns:
        BytesIO: Buffer con el archivo Excel
    """
    # Crear buffer de salida
    output = BytesIO()

    # Crear archivo Excel con openpyxl
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Crear DataFrame con estadísticas
        estadisticas = datos.get('estadisticas', {})
        if estadisticas:
            stats_data = []
            for key, value in estadisticas.items():
                # Formatear el nombre de la estadística
                label = key.replace('_', ' ').replace('total', 'Total').replace('porcentaje', 'Porcentaje').title()
                stats_data.append({'Métrica': label, 'Valor': str(value)})

            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Estadísticas', index=False)

            # Aplicar formato a la hoja de estadísticas
            ws_stats = writer.sheets['Estadísticas']
            from openpyxl.styles import Font, PatternFill, Alignment

            # Encabezados en negrita
            for cell in ws_stats[1]:
                cell.font = Font(bold=True, size=12)
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal='center')

            # Ajustar ancho de columnas
            ws_stats.column_dimensions['A'].width = 30
            ws_stats.column_dimensions['B'].width = 20

        # Crear DataFrame de datos detallados
        df = pd.DataFrame(datos['datos'])
        df.to_excel(writer, sheet_name='Datos', index=False, startrow=0)

        # Obtener la hoja de datos
        worksheet = writer.sheets['Datos']

        # Aplicar formato a encabezados
        from openpyxl.styles import Font, PatternFill, Alignment
        for cell in worksheet[1]:
            cell.font = Font(bold=True, size=11)
            cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal='center')

        # Ajustar ancho de columnas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    output.seek(0)
    return output


def exportar_a_pdf(datos, tipo_reporte):
    """
    Exporta datos a formato PDF con sumatorias y estadísticas

    Args:
        datos (dict): Datos del reporte
        tipo_reporte (str): Tipo de reporte

    Returns:
        BytesIO: Buffer con el archivo PDF
    """
    output = BytesIO()

    # Crear PDF con orientación horizontal (landscape)
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))

    # Contenedor de elementos
    elements = []

    # Estilos
    styles = getSampleStyleSheet()

    # Título
    title = Paragraph(f"<b>Reporte: {tipo_reporte.upper().replace('_', ' ').replace('-', ' ')}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))

    # Información del reporte
    info_text = f"Generado: {datos.get('fecha_generacion', '')}"
    if datos.get('año_consultado'):
        info_text += f" | Año: {datos.get('año_consultado')}"
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.3*inch))

    # Sección de Estadísticas/Sumatorias
    estadisticas = datos.get('estadisticas', {})
    if estadisticas:
        # Título de estadísticas
        stats_title = Paragraph("<b>RESUMEN Y ESTADÍSTICAS</b>", styles['Heading2'])
        elements.append(stats_title)
        elements.append(Spacer(1, 0.1*inch))

        # Crear tabla de estadísticas
        stats_data = [['Métrica', 'Valor']]
        for key, value in estadisticas.items():
            # Formatear el nombre de la estadística
            label = key.replace('_', ' ').replace('total', 'Total').replace('porcentaje', 'Porcentaje').title()
            stats_data.append([label, str(value)])

        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')])
        ]))

        elements.append(stats_table)
        elements.append(Spacer(1, 0.4*inch))

    # Título de datos detallados
    data_title = Paragraph("<b>DATOS DETALLADOS</b>", styles['Heading2'])
    elements.append(data_title)
    elements.append(Spacer(1, 0.1*inch))

    # Preparar datos para la tabla
    if datos['datos']:
        # Obtener headers
        headers = list(datos['datos'][0].keys())

        # Preparar filas
        table_data = [headers]
        for item in datos['datos']:
            row = [str(item.get(key, ''))[:30] for key in headers]  # Limitar a 30 chars
            table_data.append(row)

        # Crear tabla con tamaño dinámico
        num_cols = len(headers)
        col_width = (landscape(letter)[0] - 2*inch) / num_cols  # Distribuir ancho disponible

        table = Table(table_data, colWidths=[col_width] * num_cols)

        # Estilo de tabla
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF2CC')])
        ]))

        elements.append(table)

    # Construir PDF
    doc.build(elements)

    output.seek(0)
    return output
