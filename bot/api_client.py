import os
import coreapi

HOST = os.getenv('DB_HOST')

client = coreapi.Client()
schema = client.get(f'{HOST}/service/players')

print(schema)

