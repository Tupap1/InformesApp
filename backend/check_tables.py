from server import app, db
from sqlalchemy import text

app.app_context().push()

print('Tablas de venta:')
result = db.session.execute(text("SHOW TABLES LIKE 'venta%'")).fetchall()
for row in result:
    print(f'  {row[0]}')

print('\nTablas de dvent:')
result = db.session.execute(text("SHOW TABLES LIKE 'dvent%'")).fetchall()
for row in result:
    print(f'  {row[0]}')
