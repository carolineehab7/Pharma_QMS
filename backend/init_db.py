"""
Database initialization script with sample data
Run this script to create and populate the database with demo data
"""
import sqlite3
from datetime import datetime, timedelta
import random
from database import init_database, get_db_connection, DB_PATH


def seed_sample_data():
    """
    Populate database with sample data for demonstration
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Sample users
        users = [
            ('jsmith', 'john.smith@pharma.com', 'John Smith', 'QA Manager', 'Quality Assurance'),
            ('mjohnson', 'mary.johnson@pharma.com', 'Mary Johnson', 'Production Manager', 'Production'),
            ('rdavis', 'robert.davis@pharma.com', 'Robert Davis', 'QC Analyst', 'Quality Control'),
            ('swilson', 'sarah.wilson@pharma.com', 'Sarah Wilson', 'Regulatory Affairs', 'Regulatory'),
            ('tbrown', 'thomas.brown@pharma.com', 'Thomas Brown', 'Manufacturing Supervisor', 'Production')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO users (username, email, full_name, role, department)
            VALUES (?, ?, ?, ?, ?)
        ''', users)
        
        # Sample deviations
        deviation_categories = ['Manufacturing', 'Quality Control', 'Equipment', 'Documentation', 'Material']
        deviation_statuses = ['Open', 'Under Investigation', 'CAPA Required', 'Closed']
        
        deviations = []
        for i in range(1, 26):
            deviation_number = f'DEV-2024-{i:04d}'
            category = random.choice(deviation_categories)
            severity = random.randint(1, 10)
            occurrence = random.randint(1, 10)
            detection = random.randint(1, 10)
            rpn = severity * occurrence * detection
            status = random.choice(deviation_statuses)
            detected_date = (datetime.now() - timedelta(days=random.randint(1, 90))).date()
            
            deviations.append((
                deviation_number,
                f'{category} Deviation - Sample {i}',
                f'Sample deviation description for {category.lower()} issue.',
                category,
                severity,
                occurrence,
                detection,
                rpn,
                status,
                random.choice(['Production', 'QC Lab', 'Warehouse', 'Packaging']),
                f'BATCH-{random.randint(1000, 9999)}',
                detected_date,
                random.randint(1, 5)
            ))
        
        cursor.executemany('''
            INSERT OR IGNORE INTO deviations 
            (deviation_number, title, description, category, severity, occurrence, detection, 
             rpn, status, department, product_batch, detected_date, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', deviations)
        
        # Sample CAPA records
        capa_types = ['Corrective', 'Preventive', 'Both']
        capa_statuses = ['Open', 'In Progress', 'Pending Verification', 'Effective', 'Closed']
        
        capas = []
        for i in range(1, 16):
            capa_number = f'CAPA-2024-{i:04d}'
            capa_type = random.choice(capa_types)
            status = random.choice(capa_statuses)
            target_date = (datetime.now() + timedelta(days=random.randint(30, 90))).date()
            
            capas.append((
                capa_number,
                i,  # deviation_id
                capa_type,
                f'CAPA for Deviation {i}',
                f'Sample CAPA description for addressing deviation.',
                f'Root cause analysis: {random.choice(["Process variation", "Human error", "Equipment malfunction", "Material defect"])}',
                f'Action plan to address the root cause and prevent recurrence.',
                random.choice(['John Smith', 'Mary Johnson', 'Robert Davis']),
                target_date,
                status,
                random.randint(1, 5)
            ))
        
        cursor.executemany('''
            INSERT OR IGNORE INTO capa 
            (capa_number, deviation_id, type, title, description, root_cause, 
             action_plan, responsible_person, target_date, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', capas)
        
        # Sample monitoring data
        locations = ['Clean Room A', 'Clean Room B', 'Warehouse', 'Production Area']
        param_types = ['Environmental', 'Process']
        
        monitoring_data = []
        for _ in range(100):
            location = random.choice(locations)
            param_type = random.choice(param_types)
            
            if param_type == 'Environmental':
                params = [
                    ('Temperature', random.uniform(20, 24), '°C', 20, 24),
                    ('Humidity', random.uniform(40, 60), '%', 40, 60),
                    ('Pressure', random.uniform(10, 15), 'Pa', 10, 15)
                ]
            else:
                params = [
                    ('pH', random.uniform(6.8, 7.2), '', 6.8, 7.2),
                    ('Mixing Speed', random.uniform(95, 105), 'RPM', 95, 105),
                    ('Temperature', random.uniform(35, 40), '°C', 35, 40)
                ]
            
            param = random.choice(params)
            value = param[1]
            min_limit = param[3]
            max_limit = param[4]
            status = 'Normal' if min_limit <= value <= max_limit else 'Out of Spec'
            
            monitoring_data.append((
                location,
                param_type,
                param[0],
                value,
                param[2],
                min_limit,
                max_limit,
                status,
                'High' if status == 'Out of Spec' else 'None',
                random.randint(1, 5)
            ))
        
        cursor.executemany('''
            INSERT INTO monitoring 
            (location, parameter_type, parameter_name, value, unit, min_limit, 
             max_limit, status, alert_level, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', monitoring_data)
        
        # Sample batches
        products = [
            ('Aspirin 500mg Tablets', 'ASP-500'),
            ('Ibuprofen 200mg Capsules', 'IBU-200'),
            ('Amoxicillin 250mg Suspension', 'AMX-250'),
            ('Paracetamol 500mg Tablets', 'PAR-500')
        ]
        
        batches = []
        for i in range(1, 21):
            product = random.choice(products)
            batch_number = f'BATCH-{2024}{i:04d}'
            status = random.choice(['In Progress', 'QC Testing', 'Released', 'Quarantine'])
            start_date = (datetime.now() - timedelta(days=random.randint(1, 60))).date()
            
            batches.append((
                batch_number,
                product[0],
                product[1],
                random.randint(10000, 100000),
                'tablets' if 'Tablets' in product[0] else 'capsules' if 'Capsules' in product[0] else 'ml',
                status,
                start_date
            ))
        
        cursor.executemany('''
            INSERT OR IGNORE INTO batches 
            (batch_number, product_name, product_code, quantity, unit, status, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', batches)
        
        # Sample reports
        report_types = ['Quality', 'Deviation', 'Audit', 'Production', 'Laboratory', 'Training']
        
        reports = []
        for i in range(1, 11):
            report_type = random.choice(report_types)
            generated_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            reports.append((
                report_type,
                f'{report_type} Report - {generated_at.strftime("%B %Y")}',
                f'Monthly {report_type.lower()} report',
                '{"period": "monthly", "format": "pdf"}',
                f'/reports/{report_type.lower()}_report_{i}.pdf',
                'PDF',
                random.randint(1, 5)
            ))
        
        cursor.executemany('''
            INSERT INTO reports 
            (report_type, title, description, parameters, file_path, file_format, generated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', reports)
        
        conn.commit()
        print("Sample data inserted successfully!")


def main():
    """
    Main function to initialize database and seed data
    """
    print("=" * 60)
    print("Pharmaceutical QMS Database Initialization")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Creating database tables...")
    init_database()
    
    # Seed sample data
    print("\n2. Inserting sample data...")
    seed_sample_data()
    
    # Display summary
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("Database Summary:")
        print("=" * 60)
        
        tables = ['users', 'deviations', 'capa', 'monitoring', 'batches', 'reports']
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"{table.capitalize():20} {count:>5} records")
    
    print("\n" + "=" * 60)
    print(f"Database location: {DB_PATH}")
    print("Initialization complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
