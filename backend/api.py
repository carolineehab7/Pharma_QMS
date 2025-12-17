"""
Flask REST API Server for Pharmaceutical QMS
Provides endpoints for all database operations
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
import json
from database import get_db_connection

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# ===================================
# Helper Functions
# ===================================

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row)) if row else None


def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# ===================================
# User Endpoints
# ===================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY full_name')
        users = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(users)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = dict_from_row(cursor.fetchone())
        if user:
            return jsonify(user)
        return jsonify({'error': 'User not found'}), 404


# ===================================
# Deviation Endpoints
# ===================================

@app.route('/api/deviations', methods=['GET'])
def get_deviations():
    """Get all deviations with optional filtering"""
    status = request.args.get('status')
    category = request.args.get('category')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM deviations WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        deviations = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(deviations)


@app.route('/api/deviations/<int:deviation_id>', methods=['GET'])
def get_deviation(deviation_id):
    """Get specific deviation"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM deviations WHERE id = ?', (deviation_id,))
        deviation = dict_from_row(cursor.fetchone())
        if deviation:
            return jsonify(deviation)
        return jsonify({'error': 'Deviation not found'}), 404


@app.route('/api/deviations', methods=['POST'])
def create_deviation():
    """Create new deviation"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Calculate RPN
        rpn = data['severity'] * data['occurrence'] * data['detection']
        
        cursor.execute('''
            INSERT INTO deviations 
            (deviation_number, title, description, category, severity, occurrence, 
             detection, rpn, status, department, product_batch, detected_date, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['deviation_number'],
            data['title'],
            data['description'],
            data['category'],
            data['severity'],
            data['occurrence'],
            data['detection'],
            rpn,
            data.get('status', 'Open'),
            data.get('department'),
            data.get('product_batch'),
            data['detected_date'],
            data.get('created_by', 1)
        ))
        
        deviation_id = cursor.lastrowid
        
        # Log audit
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, changes)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('created_by', 1), 'CREATE', 'deviation', deviation_id, json.dumps(data)))
        
        return jsonify({'id': deviation_id, 'message': 'Deviation created successfully'}), 201


@app.route('/api/deviations/<int:deviation_id>', methods=['PUT'])
def update_deviation(deviation_id):
    """Update deviation"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Recalculate RPN if risk factors changed
        if 'severity' in data and 'occurrence' in data and 'detection' in data:
            data['rpn'] = data['severity'] * data['occurrence'] * data['detection']
        
        # Build update query dynamically
        fields = []
        values = []
        for key, value in data.items():
            if key not in ['id', 'created_at', 'created_by']:
                fields.append(f'{key} = ?')
                values.append(value)
        
        values.append(datetime.now())
        values.append(deviation_id)
        
        query = f"UPDATE deviations SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
        cursor.execute(query, values)
        
        # Log audit
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, changes)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('updated_by', 1), 'UPDATE', 'deviation', deviation_id, json.dumps(data)))
        
        return jsonify({'message': 'Deviation updated successfully'})


@app.route('/api/deviations/<int:deviation_id>', methods=['DELETE'])
def delete_deviation(deviation_id):
    """Delete deviation"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM deviations WHERE id = ?', (deviation_id,))
        
        # Log audit
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id)
            VALUES (?, ?, ?, ?)
        ''', (1, 'DELETE', 'deviation', deviation_id))
        
        return jsonify({'message': 'Deviation deleted successfully'})


@app.route('/api/deviations/stats', methods=['GET'])
def get_deviation_stats():
    """Get deviation statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total deviations
        cursor.execute('SELECT COUNT(*) as total FROM deviations')
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM deviations 
            GROUP BY status
        ''')
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM deviations 
            GROUP BY category
        ''')
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By risk level
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN rpn >= 200 THEN 'Critical'
                    WHEN rpn >= 100 THEN 'High'
                    WHEN rpn >= 40 THEN 'Medium'
                    ELSE 'Low'
                END as risk_level,
                COUNT(*) as count
            FROM deviations
            GROUP BY risk_level
        ''')
        by_risk = {row[0]: row[1] for row in cursor.fetchall()}
        
        return jsonify({
            'total': total,
            'by_status': by_status,
            'by_category': by_category,
            'by_risk': by_risk
        })


# ===================================
# CAPA Endpoints
# ===================================

@app.route('/api/capa', methods=['GET'])
def get_capa_records():
    """Get all CAPA records"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM capa ORDER BY created_at DESC')
        capas = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(capas)


@app.route('/api/capa/<int:capa_id>', methods=['GET'])
def get_capa(capa_id):
    """Get specific CAPA record"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM capa WHERE id = ?', (capa_id,))
        capa = dict_from_row(cursor.fetchone())
        if capa:
            return jsonify(capa)
        return jsonify({'error': 'CAPA not found'}), 404


@app.route('/api/capa', methods=['POST'])
def create_capa():
    """Create new CAPA record"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO capa 
            (capa_number, deviation_id, type, title, description, root_cause, 
             action_plan, responsible_person, target_date, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['capa_number'],
            data.get('deviation_id'),
            data['type'],
            data['title'],
            data['description'],
            data.get('root_cause'),
            data['action_plan'],
            data['responsible_person'],
            data['target_date'],
            data.get('status', 'Open'),
            data.get('created_by', 1)
        ))
        
        capa_id = cursor.lastrowid
        
        # Log audit
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, changes)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('created_by', 1), 'CREATE', 'capa', capa_id, json.dumps(data)))
        
        return jsonify({'id': capa_id, 'message': 'CAPA created successfully'}), 201


@app.route('/api/capa/<int:capa_id>', methods=['PUT'])
def update_capa(capa_id):
    """Update CAPA record"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in data.items():
            if key not in ['id', 'created_at', 'created_by']:
                fields.append(f'{key} = ?')
                values.append(value)
        
        values.append(datetime.now())
        values.append(capa_id)
        
        query = f"UPDATE capa SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
        cursor.execute(query, values)
        
        # Log audit
        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, changes)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('updated_by', 1), 'UPDATE', 'capa', capa_id, json.dumps(data)))
        
        return jsonify({'message': 'CAPA updated successfully'})


@app.route('/api/capa/by-deviation/<int:deviation_id>', methods=['GET'])
def get_capa_by_deviation(deviation_id):
    """Get CAPA records for a specific deviation"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM capa WHERE deviation_id = ?', (deviation_id,))
        capas = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(capas)


@app.route('/api/capa/stats', methods=['GET'])
def get_capa_stats():
    """Get CAPA statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total CAPA
        cursor.execute('SELECT COUNT(*) as total FROM capa')
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM capa 
            GROUP BY status
        ''')
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By type
        cursor.execute('''
            SELECT type, COUNT(*) as count 
            FROM capa 
            GROUP BY type
        ''')
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # On-time closure rate by month (last 6 months)
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', target_date) as month,
                COUNT(*) as total,
                SUM(CASE WHEN completion_date <= target_date THEN 1 ELSE 0 END) as on_time
            FROM capa
            WHERE target_date >= date('now', '-6 months')
            AND status = 'Closed'
            GROUP BY month
            ORDER BY month
        ''')
        closure_trend = []
        for row in cursor.fetchall():
            month, total_count, on_time_count = row
            percentage = round((on_time_count / total_count * 100) if total_count > 0 else 0, 1)
            closure_trend.append({
                'month': month,
                'total': total_count,
                'on_time': on_time_count,
                'percentage': percentage
            })
        
        return jsonify({
            'total': total,
            'by_status': by_status,
            'by_type': by_type,
            'closure_trend': closure_trend
        })


# ===================================
# Monitoring Endpoints
# ===================================

@app.route('/api/monitoring/environmental', methods=['GET'])
def get_environmental_monitoring():
    """Get environmental monitoring data"""
    location = request.args.get('location')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM monitoring WHERE parameter_type = 'Environmental'"
        params = []
        
        if location:
            query += ' AND location = ?'
            params.append(location)
        
        query += ' ORDER BY recorded_at DESC LIMIT 100'
        cursor.execute(query, params)
        data = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(data)


@app.route('/api/monitoring/process', methods=['GET'])
def get_process_monitoring():
    """Get process monitoring data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM monitoring 
            WHERE parameter_type = 'Process'
            ORDER BY recorded_at DESC 
            LIMIT 100
        ''')
        data = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(data)


@app.route('/api/monitoring/record', methods=['POST'])
def record_monitoring_data():
    """Record new monitoring measurement"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Determine status based on limits
        value = data['value']
        min_limit = data.get('min_limit')
        max_limit = data.get('max_limit')
        
        if min_limit and max_limit:
            status = 'Normal' if min_limit <= value <= max_limit else 'Out of Spec'
        else:
            status = 'Normal'
        
        cursor.execute('''
            INSERT INTO monitoring 
            (location, parameter_type, parameter_name, value, unit, min_limit, 
             max_limit, status, alert_level, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['location'],
            data['parameter_type'],
            data['parameter_name'],
            value,
            data.get('unit'),
            min_limit,
            max_limit,
            status,
            data.get('alert_level', 'None'),
            data.get('recorded_by', 1)
        ))
        
        return jsonify({'id': cursor.lastrowid, 'status': status}), 201


# ===================================
# Dashboard Endpoints
# ===================================

@app.route('/api/dashboard/kpis', methods=['GET'])
def get_dashboard_kpis():
    """Get key performance indicators for dashboard"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total deviations
        cursor.execute('SELECT COUNT(*) FROM deviations')
        total_deviations = cursor.fetchone()[0]
        
        # Open deviations
        cursor.execute("SELECT COUNT(*) FROM deviations WHERE status = 'Open'")
        open_deviations = cursor.fetchone()[0]
        
        # Total CAPA
        cursor.execute('SELECT COUNT(*) FROM capa')
        total_capa = cursor.fetchone()[0]
        
        # Open CAPA
        cursor.execute("SELECT COUNT(*) FROM capa WHERE status = 'Open'")
        open_capa = cursor.fetchone()[0]
        
        # Active batches
        cursor.execute("SELECT COUNT(*) FROM batches WHERE status = 'In Progress'")
        active_batches = cursor.fetchone()[0]
        
        # Out of spec monitoring
        cursor.execute("SELECT COUNT(*) FROM monitoring WHERE status = 'Out of Spec'")
        out_of_spec = cursor.fetchone()[0]
        
        return jsonify({
            'total_deviations': total_deviations,
            'open_deviations': open_deviations,
            'total_capa': total_capa,
            'open_capa': open_capa,
            'active_batches': active_batches,
            'out_of_spec_parameters': out_of_spec
        })


@app.route('/api/dashboard/trends', methods=['GET'])
def get_dashboard_trends():
    """Get trend data for charts"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Deviations by month (last 6 months)
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', detected_date) as month,
                COUNT(*) as count
            FROM deviations
            WHERE detected_date >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month
        ''')
        deviation_trend = [dict_from_row(row) for row in cursor.fetchall()]
        
        return jsonify({
            'deviation_trend': deviation_trend
        })


@app.route('/api/dashboard/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity log"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.full_name as user_name
            FROM audit_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT 20
        ''')
        activities = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(activities)


# ===================================
# Report Endpoints
# ===================================

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.full_name as generated_by_name
            FROM reports r
            LEFT JOIN users u ON r.generated_by = u.id
            ORDER BY r.generated_at DESC
        ''')
        reports = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(reports)


@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate new report"""
    data = request.json
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports 
            (report_type, title, description, parameters, file_format, generated_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['report_type'],
            data['title'],
            data.get('description'),
            json.dumps(data.get('parameters', {})),
            data.get('file_format', 'PDF'),
            data.get('generated_by', 1)
        ))
        
        report_id = cursor.lastrowid
        return jsonify({'id': report_id, 'message': 'Report generated successfully'}), 201


# ===================================
# Batch Endpoints
# ===================================

@app.route('/api/batches', methods=['GET'])
def get_batches():
    """Get all batches"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM batches ORDER BY start_date DESC')
        batches = [dict_from_row(row) for row in cursor.fetchall()]
        return jsonify(batches)


# ===================================
# Server Startup
# ===================================

@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'message': 'Pharmaceutical QMS API Server',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'deviations': '/api/deviations',
            'capa': '/api/capa',
            'monitoring': '/api/monitoring',
            'dashboard': '/api/dashboard',
            'reports': '/api/reports',
            'batches': '/api/batches'
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Pharmaceutical QMS API Server")
    print("=" * 60)
    print("Server starting on http://localhost:5001")
    print("API Documentation: http://localhost:5001")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)
