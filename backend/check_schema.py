from server import app, db
from sqlalchemy import text

app.app_context().push()

result = db.session.execute(text('DESCRIBE artic')).fetchall()
print('Columns in artic table:')
print('=' * 60)
for row in result:
    print(f'{row[0]:20} {row[1]:30}')
