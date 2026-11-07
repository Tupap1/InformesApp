from server import app, db
from sqlalchemy import text

app.app_context().push()

print('Todas las tablas en la base de datos:')
result = db.session.execute(text("SHOW TABLES")).fetchall()
for row in result:
    print(f'  {row[0]}')
