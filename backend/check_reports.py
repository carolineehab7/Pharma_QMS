import sqlite3
import json

conn = sqlite3.connect('qms_database.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT title, report_type, parameters 
    FROM reports 
    WHERE title LIKE '%Quality Metrics%' 
       OR title LIKE '%Training Compliance%' 
       OR title LIKE '%CAPA Status%' 
    ORDER BY generated_at DESC
''')

rows = cursor.fetchall()

for r in rows:
    try:
        params = json.loads(r[2] or '{}')
        if isinstance(params, str):
            params = json.loads(params)
        period = params.get('period', 'NOT FOUND')
    except Exception as e:
        period = f'ERROR: {e}'
        params = r[2]
    
    print(f'Title: {r[0]}')
    print(f'Type: {r[1]}')
    print(f'Parameters: {r[2]}')
    print(f'Period value: {period}')
    print('---')

conn.close()
