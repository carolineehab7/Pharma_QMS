"""
Quick test script to verify database contents
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'qms_database.db')

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    print("Please run: python init_db.py")
    exit(1)

# Connect and query
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE CONTENTS")
print("=" * 60)

# Count records in each table
tables = ['users', 'deviations', 'capa', 'monitoring', 'batches', 'reports']
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f"{table.upper():20} {count:>5} records")

print("\n" + "=" * 60)
print("SAMPLE DEVIATIONS")
print("=" * 60)

cursor.execute('''
    SELECT deviation_number, title, category, status, rpn 
    FROM deviations 
    ORDER BY created_at DESC 
    LIMIT 5
''')

for row in cursor.fetchall():
    print(f"\n{row[0]}")
    print(f"  Title: {row[1]}")
    print(f"  Category: {row[2]}")
    print(f"  Status: {row[3]}")
    print(f"  RPN: {row[4]}")

print("\n" + "=" * 60)
print(f"Database location: {db_path}")
print("=" * 60)

conn.close()
