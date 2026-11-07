from server import app, Artic

app.app_context().push()

print('Testing Artic model query...')
count = Artic.query.limit(5).count()
print(f'✓ Successfully queried {count} records from ARTIC table')

if count > 0:
    first_record = Artic.query.first()
    print(f'\nSample record:')
    print(f'  Código: {first_record.ARTCOD}')
    print(f'  Existencia: {first_record.ARTEXI}')
    print(f'  Precio: {first_record.ARTPRE}')
