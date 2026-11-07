from server import app, reporte_inventario

app.app_context().push()

print('Testing reporte_inventario function...')
try:
    result = reporte_inventario(estado='ACT')
    print(f'✓ Successfully generated report')
    print(f'Total items: {result["estadisticas"]["totalItems"]}')
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
