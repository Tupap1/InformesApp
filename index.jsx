import React, { useState, useEffect } from 'react';
import {
  Search,
  Package,
  TrendingUp,
  Calendar,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Filter,
  Download,
  RefreshCw,
  FileSpreadsheet,
  FileText,
  ShoppingCart,
  PiggyBank
} from 'lucide-react';

/**
 * Dashboard de Reportes - Sistema de Inventario y Ventas
 * Componente principal que integra con el backend Flask
 */
const ReportesDashboard = () => {
  // ========================================
  // ESTADO DEL COMPONENTE
  // ========================================

  const [reporteActivo, setReporteActivo] = useState('inventario');
  const [filtros, setFiltros] = useState({
    codigo: '',
    sucursal: '',
    proveedor: '',
    grupo: '',
    fechaInicio: '',
    fechaFin: '',
    estado: 'ACT',
    ubicacion: ''
  });
  const [datos, setDatos] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [mostrarFiltros, setMostrarFiltros] = useState(true);

  // Estado para columnas opcionales en reporte de ventas
  const [columnasVentas, setColumnasVentas] = useState({
    estado: true,
    fe: true,
    unidadesNarradas: true
  });

  // Estado para modal de detalle de venta
  const [modalDetalle, setModalDetalle] = useState({
    visible: false,
    numeroVenta: null,
    productos: [],
    cargando: false
  });

  // Estado para opciones de exportación de ventas
  const [opcionesExportacion, setOpcionesExportacion] = useState({
    incluir_narradas: false,
    detalle_productos: false
  });

  // Estado para modal de vista previa
  const [modalVistaPrevia, setModalVistaPrevia] = useState({
    visible: false,
    datos: [],
    estadisticas: {},
    formato: 'excel', // 'excel' o 'pdf'
    cargando: false
  });

  // URL base del API
  const API_BASE_URL = 'http://localhost:5000';

  // ========================================
  // UTILIDADES DE FORMATO
  // ========================================

  /**
   * Formatea números grandes con sufijos K (miles), M (millones), B (miles de millones)
   * @param {number} num - Número a formatear
   * @returns {string} - Número formateado con sufijo
   */
  const formatNumber = (num) => {
    if (num === null || num === undefined || num === '') return '0';

    // Si es string (viene formateado del backend), retornar tal cual
    if (typeof num === 'string') return num;

    const absNum = Math.abs(num);
    const isNegative = num < 0;

    let formatted;
    if (absNum >= 1000000000) {
      formatted = (absNum / 1000000000).toFixed(2) + 'B';
    } else if (absNum >= 1000000) {
      formatted = (absNum / 1000000).toFixed(2) + 'M';
    } else if (absNum >= 10000) {
      formatted = (absNum / 1000).toFixed(2) + 'K';
    } else {
      formatted = absNum.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    return isNegative ? '-' + formatted : formatted;
  };

  // ========================================
  // FUNCIONES DE FETCH Y MANEJO DE DATOS
  // ========================================

  /**
   * Construye la URL del API con los parámetros de filtro
   */
  const construirURL = () => {
    const params = new URLSearchParams();

    // Determinar el endpoint correcto según el tipo de reporte
    let endpoint = '/api/reportes';

    if (reporteActivo === 'productos-vendidos') {
      endpoint = '/api/reportes/productos-vendidos';
    } else if (reporteActivo === 'utilidad') {
      endpoint = '/api/reportes/utilidad';
    } else {
      // Para inventario y ventas, usar el endpoint original
      params.append('tipo', reporteActivo);
    }

    // Agregar filtros solo si tienen valor
    Object.entries(filtros).forEach(([key, value]) => {
      if (value && value.trim() !== '') {
        params.append(key, value);
      }
    });

    return `${API_BASE_URL}${endpoint}?${params.toString()}`;
  };

  /**
   * Realiza la petición al API para obtener el reporte
   */
  const fetchReporte = async () => {
    setCargando(true);
    setError(null);

    try {
      const url = construirURL();
      console.log('Fetching:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const data = await response.json();

      setDatos(data.datos || []);
      setEstadisticas(data.estadisticas || {});

      console.log('Datos recibidos:', data);
    } catch (err) {
      console.error('Error al obtener reporte:', err);
      setError(`Error al cargar el reporte: ${err.message}`);
      setDatos([]);
      setEstadisticas({});
    } finally {
      setCargando(false);
    }
  };

  /**
   * Maneja el cambio de valores en los filtros
   */
  const handleFiltroChange = (campo, valor) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }));
  };

  /**
   * Limpia todos los filtros
   */
  const limpiarFiltros = () => {
    setFiltros({
      codigo: '',
      sucursal: '',
      proveedor: '',
      grupo: '',
      fechaInicio: '',
      fechaFin: '',
      estado: 'ACT',
      ubicacion: ''
    });
  };

  /**
   * Cambia el tipo de reporte activo
   */
  const cambiarReporte = (tipo) => {
    setReporteActivo(tipo);
    setDatos([]);
    setEstadisticas({});
    setError(null);
  };

  /**
   * Carga el detalle de productos de una venta específica
   */
  const cargarDetalleVenta = async (numeroVenta) => {
    setModalDetalle(prev => ({ ...prev, cargando: true, visible: true, numeroVenta }));

    try {
      const params = new URLSearchParams();
      if (filtros.fechaInicio) params.append('fechaInicio', filtros.fechaInicio);
      if (filtros.fechaFin) params.append('fechaFin', filtros.fechaFin);

      const url = `${API_BASE_URL}/api/detalle_venta/${numeroVenta}?${params.toString()}`;
      console.log('Cargando detalle de venta:', url);

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const data = await response.json();
      setModalDetalle(prev => ({
        ...prev,
        productos: data.productos || [],
        cargando: false
      }));

      console.log('Detalle de venta cargado:', data);
    } catch (err) {
      console.error('Error al cargar detalle de venta:', err);
      alert(`Error al cargar el detalle: ${err.message}`);
      setModalDetalle(prev => ({ ...prev, cargando: false, visible: false }));
    }
  };

  /**
   * Cierra el modal de detalle
   */
  const cerrarModalDetalle = () => {
    setModalDetalle({
      visible: false,
      numeroVenta: null,
      productos: [],
      cargando: false
    });
  };

  /**
   * Exporta los datos a CSV
   */
  const exportarCSV = () => {
    if (datos.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    const headers = Object.keys(datos[0]).join(',');
    const rows = datos.map(item =>
      Object.values(item).map(val =>
        typeof val === 'object' ? JSON.stringify(val) : val
      ).join(',')
    ).join('\n');

    const csv = `${headers}\n${rows}`;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reporte_${reporteActivo}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  /**
   * Exporta el reporte a Excel
   */
  const exportarExcel = () => {
    mostrarVistaPrevia('excel');
  };

  /**
   * Exporta el reporte a PDF
   */
  const exportarPDF = () => {
    mostrarVistaPrevia('pdf');
  };

  /**
   * Muestra vista previa antes de exportar
   */
  const mostrarVistaPrevia = async (formato) => {
    if (datos.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    setModalVistaPrevia({
      visible: true,
      datos: [],
      estadisticas: {},
      formato: formato,
      cargando: true
    });

    try {
      // Construir URL con todos los filtros
      const params = new URLSearchParams();
      params.append('tipo', reporteActivo);

      Object.entries(filtros).forEach(([key, value]) => {
        if (value && value.trim() !== '') {
          params.append(key, value);
        }
      });

      // Agregar opciones de exportación para ventas
      if (reporteActivo === 'ventas') {
        params.append('incluir_narradas', opcionesExportacion.incluir_narradas);
        params.append('detalle_productos', opcionesExportacion.detalle_productos);
      }

      const url = `${API_BASE_URL}/api/vista-previa?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Error al obtener vista previa');
      }

      const data = await response.json();

      setModalVistaPrevia({
        visible: true,
        datos: data.datos || [],
        estadisticas: data.estadisticas || {},
        formato: formato,
        cargando: false,
        nota: data.nota || null
      });

    } catch (error) {
      console.error('Error al cargar vista previa:', error);
      alert('Error al cargar vista previa: ' + error.message);
      setModalVistaPrevia({
        visible: false,
        datos: [],
        estadisticas: {},
        formato: 'excel',
        cargando: false
      });
    }
  };

  /**
   * Confirma y ejecuta la exportación
   */
  const confirmarExportacion = () => {
    const { formato } = modalVistaPrevia;

    // Construir URL con todos los filtros
    const params = new URLSearchParams();
    params.append('tipo', reporteActivo);
    params.append('formato', formato);

    Object.entries(filtros).forEach(([key, value]) => {
      if (value && value.trim() !== '') {
        params.append(key, value);
      }
    });

    // Agregar opciones de exportación para ventas
    if (reporteActivo === 'ventas') {
      params.append('incluir_narradas', opcionesExportacion.incluir_narradas);
      params.append('detalle_productos', opcionesExportacion.detalle_productos);
    }

    // Descargar el archivo
    const url = `${API_BASE_URL}/api/exportar?${params.toString()}`;
    window.open(url, '_blank');

    // Cerrar modal
    setModalVistaPrevia({
      visible: false,
      datos: [],
      estadisticas: {},
      formato: 'excel',
      cargando: false
    });
  };

  // Cargar datos inicialmente
  useEffect(() => {
    fetchReporte();
  }, [reporteActivo]);

  // ========================================
  // COMPONENTES INTERNOS
  // ========================================

  /**
   * Panel de estadísticas agregadas
   */
  const PanelEstadisticas = () => {
    if (!estadisticas || Object.keys(estadisticas).length === 0) {
      return null;
    }

    const statsInventario = [
      {
        label: 'Total Items',
        value: formatNumber(estadisticas.totalItems),
        icon: Package,
        color: 'blue'
      },
      {
        label: 'Total Existencias',
        value: formatNumber(estadisticas.totalExistencias),
        icon: TrendingUp,
        color: 'green'
      },
      {
        label: 'Valor Total (Costo)',
        value: `$${formatNumber(estadisticas.valorTotalCosto)}`,
        icon: DollarSign,
        color: 'yellow'
      },
      {
        label: 'Valor Total (Venta)',
        value: `$${formatNumber(estadisticas.valorTotalVenta)}`,
        icon: DollarSign,
        color: 'purple'
      },
      {
        label: 'Utilidad Potencial',
        value: `$${formatNumber(estadisticas.utilidadPotencial)}`,
        icon: CheckCircle,
        color: 'green'
      }
    ];

    const statsVentas = [
      {
        label: 'Total Transacciones',
        value: formatNumber(estadisticas.totalTransacciones),
        icon: Package,
        color: 'blue'
      },
      {
        label: 'Cantidad Vendida',
        value: formatNumber(estadisticas.cantidadTotalVendida),
        icon: TrendingUp,
        color: 'green'
      },
      {
        label: 'Valor Total Ventas',
        value: `$${formatNumber(estadisticas.valorTotalVentas)}`,
        icon: DollarSign,
        color: 'purple'
      }
    ];

    const statsProductosVendidos = [
      {
        label: 'Total Productos',
        value: formatNumber(estadisticas.totalProductos),
        icon: Package,
        color: 'blue'
      },
      {
        label: 'Total Vendido',
        value: formatNumber(estadisticas.totalVendido),
        icon: ShoppingCart,
        color: 'green'
      }
    ];

    const statsUtilidad = [
      {
        label: 'Total Productos',
        value: formatNumber(estadisticas.totalProductos),
        icon: Package,
        color: 'blue'
      },
      {
        label: 'Total Ventas',
        value: `$${formatNumber(estadisticas.totalVentas)}`,
        icon: DollarSign,
        color: 'purple'
      },
      {
        label: 'Ganancia Total',
        value: `$${formatNumber(estadisticas.totalGananciaPesos)}`,
        icon: PiggyBank,
        color: 'green'
      },
      {
        label: 'Ganancia %',
        value: estadisticas.porcentajeGananciaTotal || '0%',
        icon: TrendingUp,
        color: 'yellow'
      }
    ];

    let stats;
    if (reporteActivo === 'inventario') {
      stats = statsInventario;
    } else if (reporteActivo === 'ventas') {
      stats = statsVentas;
    } else if (reporteActivo === 'productos-vendidos') {
      stats = statsProductosVendidos;
    } else if (reporteActivo === 'utilidad') {
      stats = statsUtilidad;
    } else {
      stats = statsVentas; // Fallback
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          const colorClasses = {
            blue: 'bg-blue-100 text-blue-600',
            green: 'bg-green-100 text-green-600',
            yellow: 'bg-yellow-100 text-yellow-600',
            purple: 'bg-purple-100 text-purple-600'
          };

          return (
            <div key={index} className="bg-white rounded-lg shadow p-4 border border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 font-medium">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-full ${colorClasses[stat.color]}`}>
                  <Icon size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  /**
   * Formulario de filtros
   */
  const FormularioFiltros = () => {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-200 transition-all duration-300 ${mostrarFiltros ? '' : 'hidden'}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <Filter size={20} />
            Filtros de Búsqueda
          </h3>
          <button
            onClick={limpiarFiltros}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Limpiar Filtros
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Código / Número de Venta */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {reporteActivo === 'ventas' ? 'Número de Venta' : 'Código Producto'}
            </label>
            <input
              type="text"
              value={filtros.codigo}
              onChange={(e) => handleFiltroChange('codigo', e.target.value)}
              placeholder={reporteActivo === 'ventas' ? 'Ej: 12345' : 'Ej: PROD001'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Sucursal */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sucursal
            </label>
            <input
              type="text"
              value={filtros.sucursal}
              onChange={(e) => handleFiltroChange('sucursal', e.target.value)}
              placeholder="Ej: 01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Proveedor */}
          {(reporteActivo === 'inventario' || reporteActivo === 'productos-vendidos' || reporteActivo === 'utilidad') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Proveedor
              </label>
              <input
                type="text"
                value={filtros.proveedor}
                onChange={(e) => handleFiltroChange('proveedor', e.target.value)}
                placeholder="Código proveedor"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Grupo */}
          {(reporteActivo === 'productos-vendidos' || reporteActivo === 'utilidad') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Grupo
              </label>
              <input
                type="text"
                value={filtros.grupo}
                onChange={(e) => handleFiltroChange('grupo', e.target.value)}
                placeholder="Código grupo"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Estado (solo para inventario) */}
          {reporteActivo === 'inventario' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estado
              </label>
              <select
                value={filtros.estado}
                onChange={(e) => handleFiltroChange('estado', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="ACT">Activo</option>
                <option value="INA">Inactivo</option>
                <option value="SUS">Suspendido</option>
              </select>
            </div>
          )}

          {/* Ubicación */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ubicación
            </label>
            <input
              type="text"
              value={filtros.ubicacion}
              onChange={(e) => handleFiltroChange('ubicacion', e.target.value)}
              placeholder="Código ubicación"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fecha Inicio */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Inicio
            </label>
            <input
              type="date"
              value={filtros.fechaInicio}
              onChange={(e) => handleFiltroChange('fechaInicio', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Fecha Fin */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Fin
            </label>
            <input
              type="date"
              value={filtros.fechaFin}
              onChange={(e) => handleFiltroChange('fechaFin', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="mt-4 space-y-3">
          {/* Botón principal: Aplicar Filtros */}
          <button
            onClick={fetchReporte}
            disabled={cargando}
            className="w-full bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
          >
            {cargando ? (
              <>
                <RefreshCw size={18} className="animate-spin" />
                Cargando...
              </>
            ) : (
              <>
                <Search size={18} />
                Aplicar Filtros
              </>
            )}
          </button>

          {/* Opciones de Exportación para Ventas */}
          {reporteActivo === 'ventas' && (
            <div className="col-span-full bg-blue-50 border border-blue-200 rounded-md p-3 mb-2">
              <p className="text-sm font-medium text-gray-700 mb-2">Opciones de Exportación:</p>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={opcionesExportacion.incluir_narradas}
                    onChange={(e) => setOpcionesExportacion(prev => ({ ...prev, incluir_narradas: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Incluir Unidades Narradas</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={opcionesExportacion.detalle_productos}
                    onChange={(e) => setOpcionesExportacion(prev => ({ ...prev, detalle_productos: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Detalle por Productos</span>
                </label>
              </div>
            </div>
          )}

          {/* Botones de Exportación */}
          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={exportarCSV}
              disabled={datos.length === 0}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm"
            >
              <Download size={16} />
              CSV
            </button>
            <button
              onClick={exportarExcel}
              disabled={datos.length === 0}
              className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm"
            >
              <FileSpreadsheet size={16} />
              Excel
            </button>
            <button
              onClick={exportarPDF}
              disabled={datos.length === 0}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium text-sm"
            >
              <FileText size={16} />
              PDF
            </button>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Tabla de resultados para Inventario
   */
  const TablaInventario = () => {
    if (datos.length === 0) {
      return (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <Package size={48} className="mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">No se encontraron resultados</p>
          <p className="text-sm text-gray-500 mt-1">Ajusta los filtros e intenta nuevamente</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Existencia</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Disponible</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Costo</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Valor Inv.</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proveedor</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Alertas</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {datos.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{item.codigo}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{item.nombreProducto}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">{item.descripcionProducto}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-gray-900">{item.existencia}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">{item.disponible}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${item.costoPromedio?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${item.precioVenta?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-blue-600">
                    ${item.valorInventario?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{item.proveedor}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      item.estado === 'ACT' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {item.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    {item.alertas?.bajoPuntoMinimo && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertTriangle size={12} className="mr-1" />
                        Bajo
                      </span>
                    )}
                    {item.alertas?.puntoReorden && !item.alertas?.bajoPuntoMinimo && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        <AlertTriangle size={12} className="mr-1" />
                        Reorden
                      </span>
                    )}
                    {!item.alertas?.bajoPuntoMinimo && !item.alertas?.puntoReorden && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle size={12} className="mr-1" />
                        OK
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-semibold">{datos.length}</span> resultados
          </p>
        </div>
      </div>
    );
  };

  /**
   * Tabla de resultados para Ventas
   */
  const TablaVentas = () => {
    if (datos.length === 0) {
      return (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <TrendingUp size={48} className="mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">No se encontraron resultados</p>
          <p className="text-sm text-gray-500 mt-1">Ajusta los filtros e intenta nuevamente</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Controles de columnas opcionales */}
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Mostrar columnas:</span>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={columnasVentas.estado}
                onChange={(e) => setColumnasVentas(prev => ({ ...prev, estado: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Estado</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={columnasVentas.fe}
                onChange={(e) => setColumnasVentas(prev => ({ ...prev, fe: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">FE</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={columnasVentas.unidadesNarradas}
                onChange={(e) => setColumnasVentas(prev => ({ ...prev, unidadesNarradas: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Unidades Narradas</span>
            </label>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre Cliente</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Productos</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Base Grabable</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Impuesto</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                {columnasVentas.estado && (
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                )}
                {columnasVentas.fe && (
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">FE</th>
                )}
                {columnasVentas.unidadesNarradas && (
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Un. Narradas</th>
                )}
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {datos.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-blue-600">
                    {item.codigo}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">{item.nombreCliente}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{item.nombreProducto}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-center text-gray-600">
                    <div className="flex items-center justify-center gap-1">
                      <Calendar size={14} />
                      {item.fechaVenta}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${item.baseGrabable?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${item.impuesto?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-bold text-green-600">
                    ${item.valorTotal?.toFixed(2)}
                  </td>
                  {columnasVentas.estado && (
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-center text-gray-600">
                      {item.estado}
                    </td>
                  )}
                  {columnasVentas.fe && (
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-center text-gray-600">
                      {item.fe}
                    </td>
                  )}
                  {columnasVentas.unidadesNarradas && (
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-center text-gray-600">
                      {item.unidadesNarradas}
                    </td>
                  )}
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                    <button
                      onClick={() => cargarDetalleVenta(item.codigo)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs px-3 py-1 rounded border border-blue-300 hover:bg-blue-50 transition-colors"
                    >
                      Ver Detalle
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-semibold">{datos.length}</span> ventas
          </p>
        </div>
      </div>
    );
  };

  /**
   * Tabla de resultados para Productos Vendidos
   */
  const TablaProductosVendidos = () => {
    if (datos.length === 0) {
      return (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <ShoppingCart size={48} className="mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">No se encontraron resultados</p>
          <p className="text-sm text-gray-500 mt-1">Ajusta los filtros e intenta nuevamente</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Cant. Vendida</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Precio Prom.</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Valor Total</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Existencias</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Marca</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proveedor</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {datos.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{item.codigo}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{item.descripcion}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-blue-600">
                    {item.cuantos_se_vendio?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${formatNumber(item.precio_promedio)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-bold text-green-600">
                    ${formatNumber(item.valor_total_vendido)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {item.existencias?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{item.marca}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{item.proveedor}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-semibold">{datos.length}</span> productos
          </p>
        </div>
      </div>
    );
  };

  /**
   * Tabla de resultados para Utilidad
   */
  const TablaUtilidad = () => {
    if (datos.length === 0) {
      return (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <PiggyBank size={48} className="mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">No se encontraron resultados</p>
          <p className="text-sm text-gray-500 mt-1">Ajusta los filtros e intenta nuevamente</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descripción</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Cant. Vendida</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Costo</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Precio Venta</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total Ventas</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ganancia $</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ganancia %</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {datos.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{item.codigo}</td>
                  <td className="px-4 py-3 text-sm text-gray-900">{item.descripcion}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    {item.cuantos_se_vendio?.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${formatNumber(item.costo)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                    ${formatNumber(item.precio_de_venta)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-blue-600">
                    ${formatNumber(item.total_ventas)}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-sm text-right font-bold ${
                    item.ganancia_en_pesos >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${formatNumber(item.ganancia_en_pesos)}
                  </td>
                  <td className={`px-4 py-3 whitespace-nowrap text-sm text-right font-bold ${
                    item.ganancias_en_porcentaje >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {item.ganancias_en_porcentaje?.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Mostrando <span className="font-semibold">{datos.length}</span> productos
          </p>
        </div>
      </div>
    );
  };

  // ========================================
  // MODAL DE VISTA PREVIA
  // ========================================

  const ModalVistaPrevia = () => {
    if (!modalVistaPrevia.visible) return null;

    const { datos: datosPreview, estadisticas: statsPreview, formato, cargando, nota } = modalVistaPrevia;

    return (
      <div className="fixed inset-0 z-50 overflow-y-auto" onClick={() => setModalVistaPrevia({ ...modalVistaPrevia, visible: false })}>
        <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          {/* Overlay oscuro */}
          <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" aria-hidden="true"></div>

          {/* Centro modal */}
          <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

          {/* Modal */}
          <div
            className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-6xl sm:w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 className="text-2xl leading-6 font-bold text-gray-900 mb-4">
                    Vista Previa - Exportación a {formato.toUpperCase()}
                  </h3>

                  {cargando ? (
                    <div className="flex justify-center items-center py-12">
                      <RefreshCw className="animate-spin h-12 w-12 text-blue-600" />
                      <span className="ml-4 text-lg text-gray-600">Cargando vista previa...</span>
                    </div>
                  ) : (
                    <>
                      {/* Nota si hay */}
                      {nota && (
                        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                          <p className="text-sm text-yellow-800">ℹ️ {nota}</p>
                        </div>
                      )}

                      {/* Estadísticas */}
                      {statsPreview && Object.keys(statsPreview).length > 0 && (
                        <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                          {Object.entries(statsPreview).map(([key, value]) => (
                            <div key={key} className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                              <p className="text-xs text-blue-600 font-semibold uppercase">{key.replace(/([A-Z])/g, ' $1').trim()}</p>
                              <p className="text-lg font-bold text-blue-900">
                                {typeof value === 'object' ? JSON.stringify(value) : (typeof value === 'number' ? formatNumber(value) : value)}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Tabla de datos */}
                      {datosPreview && datosPreview.length > 0 && (
                        <div className="overflow-x-auto max-h-96 border border-gray-300 rounded-lg">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-100 sticky top-0">
                              <tr>
                                {Object.keys(datosPreview[0]).map((key) => (
                                  <th
                                    key={key}
                                    className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
                                  >
                                    {key.replace(/_/g, ' ')}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {datosPreview.map((row, idx) => (
                                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                  {Object.values(row).map((value, colIdx) => (
                                    <td key={colIdx} className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                                      {typeof value === 'object' && value !== null
                                        ? JSON.stringify(value)
                                        : typeof value === 'number'
                                        ? formatNumber(value)
                                        : value || '-'}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Botones del modal */}
            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-3">
              <button
                type="button"
                onClick={confirmarExportacion}
                disabled={cargando}
                className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-6 py-3 bg-blue-600 text-base font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="mr-2 h-5 w-5" />
                Confirmar y Exportar
              </button>
              <button
                type="button"
                onClick={() => setModalVistaPrevia({ ...modalVistaPrevia, visible: false })}
                className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-6 py-3 bg-white text-base font-semibold text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ========================================
  // RENDER PRINCIPAL
  // ========================================

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard de Reportes</h1>
          <p className="text-gray-600">Sistema de gestión de inventario y ventas</p>
        </div>

        {/* Pestañas de Tipo de Reporte */}
        <div className="bg-white rounded-lg shadow mb-6 p-2 grid grid-cols-2 md:grid-cols-4 gap-2">
          <button
            onClick={() => cambiarReporte('inventario')}
            className={`py-3 px-4 rounded-md font-semibold transition-colors flex items-center justify-center gap-2 ${
              reporteActivo === 'inventario'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Package size={20} />
            <span className="hidden sm:inline">Inventario</span>
          </button>
          <button
            onClick={() => cambiarReporte('ventas')}
            className={`py-3 px-4 rounded-md font-semibold transition-colors flex items-center justify-center gap-2 ${
              reporteActivo === 'ventas'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <TrendingUp size={20} />
            <span className="hidden sm:inline">Ventas</span>
          </button>
          <button
            onClick={() => cambiarReporte('productos-vendidos')}
            className={`py-3 px-4 rounded-md font-semibold transition-colors flex items-center justify-center gap-2 ${
              reporteActivo === 'productos-vendidos'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ShoppingCart size={20} />
            <span className="hidden sm:inline">Productos Vendidos</span>
          </button>
          <button
            onClick={() => cambiarReporte('utilidad')}
            className={`py-3 px-4 rounded-md font-semibold transition-colors flex items-center justify-center gap-2 ${
              reporteActivo === 'utilidad'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <PiggyBank size={20} />
            <span className="hidden sm:inline">Utilidad</span>
          </button>
        </div>

        {/* Toggle Filtros */}
        <button
          onClick={() => setMostrarFiltros(!mostrarFiltros)}
          className="mb-4 text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2"
        >
          <Filter size={18} />
          {mostrarFiltros ? 'Ocultar Filtros' : 'Mostrar Filtros'}
        </button>

        {/* Formulario de Filtros */}
        <FormularioFiltros />

        {/* Mensaje de Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
            <AlertTriangle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Panel de Estadísticas */}
        <PanelEstadisticas />

        {/* Tabla de Resultados */}
        <div className="mb-6">
          {cargando ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <RefreshCw size={48} className="mx-auto text-blue-600 animate-spin mb-4" />
              <p className="text-gray-600 font-medium">Cargando datos...</p>
            </div>
          ) : (
            <>
              {reporteActivo === 'inventario' && <TablaInventario />}
              {reporteActivo === 'ventas' && <TablaVentas />}
              {reporteActivo === 'productos-vendidos' && <TablaProductosVendidos />}
              {reporteActivo === 'utilidad' && <TablaUtilidad />}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 mt-8">
          <p>Sistema de Reportes v2.1 - Made by btw-one©</p>
        </div>
      </div>

      {/* Modal de Detalle de Venta */}
      {modalDetalle.visible && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            {/* Header del Modal */}
            <div className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                Detalle de Venta #{modalDetalle.numeroVenta}
              </h2>
              <button
                onClick={cerrarModalDetalle}
                className="text-white hover:bg-blue-700 rounded-full p-2 transition-colors"
              >
                <span className="text-2xl leading-none">×</span>
              </button>
            </div>

            {/* Contenido del Modal */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {modalDetalle.cargando ? (
                <div className="text-center py-12">
                  <RefreshCw size={48} className="mx-auto text-blue-600 animate-spin mb-4" />
                  <p className="text-gray-600">Cargando productos...</p>
                </div>
              ) : modalDetalle.productos.length === 0 ? (
                <div className="text-center py-12">
                  <Package size={48} className="mx-auto text-gray-400 mb-3" />
                  <p className="text-gray-600">No se encontraron productos para esta venta</p>
                </div>
              ) : (
                <div>
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      Total de productos: <span className="font-semibold">{modalDetalle.productos.length}</span>
                    </p>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Código
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Producto
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Cantidad
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Precio Unit.
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Descuento
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Impuesto
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Total
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {modalDetalle.productos.map((producto, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                              {producto.codigoProducto}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {producto.nombreProducto}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              {producto.cantidad?.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              ${producto.precioUnitario?.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              ${producto.descuentoLinea?.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                              ${producto.impuestoLinea?.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                              ${producto.valorLinea?.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* Footer del Modal */}
            <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={cerrarModalDetalle}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Vista Previa */}
      <ModalVistaPrevia />
    </div>
  );
};

export default ReportesDashboard;
