"""
PyInstaller Runtime Hook para Numpy
Limpia el entorno antes de importar numpy para evitar conflictos
"""
import os
import sys

# Limpiar cualquier variable de entorno que pueda confundir a numpy
if 'NUMPY_EXPERIMENTAL_ARRAY_FUNCTION' in os.environ:
    del os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION']

# Asegurar que numpy no crea que está en su directorio fuente
# Esto soluciona el error "you should not try to import numpy from its source directory"
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    # Estamos en un ejecutable empaquetado de PyInstaller
    # Forzar que numpy use el path correcto
    import importlib.util

    # Pre-importar numpy.core para evitar problemas de importación circular
    try:
        # Limpiar cualquier importación parcial previa
        modules_to_clean = [key for key in sys.modules.keys() if key.startswith('numpy')]
        for mod in modules_to_clean:
            if 'setup' in mod.lower() or 'test' in mod.lower():
                del sys.modules[mod]
    except:
        pass
