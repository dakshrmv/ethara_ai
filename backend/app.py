from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db_connection, init_db
import os

app = Flask(__name__)
CORS(app)

# Initialize DB
with app.app_context():
    init_db()

# --- Serve Frontend ---
FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    if os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# --- API Endpoints ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    with get_db_connection() as conn:
        from sqlalchemy import text
        result = conn.execute(text('SELECT * FROM users WHERE username = :u AND password = :p'), {"u": username, "p": password}).fetchone()
        
        if result:
            user = result._mapping
            return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/projects', methods=['GET', 'POST'])
def handle_projects():
    from sqlalchemy import text
    with get_db_connection() as conn:
        if request.method == 'POST':
            data = request.json
            result = conn.execute(text('INSERT INTO projects (name, description) VALUES (:name, :desc) RETURNING id'), 
                                  {"name": data['name'], "desc": data.get('description', '')})
            project_id = result.scalar()
            conn.commit()
            return jsonify({'id': project_id, 'name': data['name'], 'description': data.get('description')}), 201
        else:
            projects = conn.execute(text('SELECT * FROM projects')).fetchall()
            return jsonify([dict(p._mapping) for p in projects])

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    from sqlalchemy import text
    with get_db_connection() as conn:
        conn.execute(text('DELETE FROM projects WHERE id = :id'), {"id": project_id})
        conn.commit()
        return jsonify({'success': True})

@app.route('/projects/<int:project_id>/tasks', methods=['GET', 'POST'])
def handle_tasks(project_id):
    from sqlalchemy import text
    with get_db_connection() as conn:
        if request.method == 'POST':
            data = request.json
            result = conn.execute(text('''
                INSERT INTO tasks (title, description, status, due_date, project_id, assigned_to) 
                VALUES (:title, :desc, :status, :due, :pid, :assign) RETURNING id
            '''), {
                "title": data['title'], 
                "desc": data.get('description', ''), 
                "status": 'TODO', 
                "due": data.get('due_date'), 
                "pid": project_id, 
                "assign": data.get('assigned_to')
            })
            task_id = result.scalar()
            conn.commit()
            return jsonify({'id': task_id}), 201
        else:
            tasks = conn.execute(text('SELECT * FROM tasks WHERE project_id = :pid'), {"pid": project_id}).fetchall()
            return jsonify([dict(t._mapping) for t in tasks])

@app.route('/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def update_task(task_id):
    from sqlalchemy import text
    with get_db_connection() as conn:
        if request.method == 'PUT':
            data = request.json
            conn.execute(text('UPDATE tasks SET status = :status WHERE id = :id'), {"status": data['status'], "id": task_id})
            conn.commit()
            return jsonify({'success': True})
        elif request.method == 'DELETE':
            conn.execute(text('DELETE FROM tasks WHERE id = :id'), {"id": task_id})
            conn.commit()
            return jsonify({'success': True})

@app.route('/users', methods=['GET'])
def get_users():
    from sqlalchemy import text
    with get_db_connection() as conn:
        users = conn.execute(text('SELECT id, username, role FROM users')).fetchall()
        return jsonify([dict(u._mapping) for u in users])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
