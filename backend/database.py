"""
Database connection and initialization module for Pharmaceutical QMS
"""
import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'qms_database.db')


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Ensures connections are properly closed
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """
    Initialize the database with all required tables
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Deviations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deviations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deviation_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                severity INTEGER NOT NULL,
                occurrence INTEGER NOT NULL,
                detection INTEGER NOT NULL,
                rpn INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                department TEXT,
                product_batch TEXT,
                detected_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        # CAPA (Corrective and Preventive Actions) table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capa_number TEXT UNIQUE NOT NULL,
                deviation_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                root_cause TEXT,
                action_plan TEXT NOT NULL,
                responsible_person TEXT NOT NULL,
                target_date DATE NOT NULL,
                completion_date DATE,
                status TEXT NOT NULL DEFAULT 'Open',
                effectiveness TEXT,
                verification_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (deviation_id) REFERENCES deviations(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                parameters TEXT,
                file_path TEXT,
                file_format TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generated_by INTEGER,
                FOREIGN KEY (generated_by) REFERENCES users(id)
            )
        ''')
        
        # Monitoring data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                parameter_type TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                min_limit REAL,
                max_limit REAL,
                status TEXT NOT NULL,
                alert_level TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recorded_by INTEGER,
                FOREIGN KEY (recorded_by) REFERENCES users(id)
            )
        ''')
        
        # Audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                changes TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Batches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_number TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                product_code TEXT,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'In Progress',
                start_date DATE NOT NULL,
                completion_date DATE,
                release_date DATE,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                document_type TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Draft',
                effective_date DATE,
                review_date DATE,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully!")


def drop_all_tables():
    """
    Drop all tables - use with caution!
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        tables = ['audit_logs', 'monitoring', 'reports', 'capa', 'deviations', 
                  'documents', 'batches', 'users']
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        conn.commit()
        print("All tables dropped!")


if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print(f"Database created at: {DB_PATH}")
