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
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        return jsonify({'success': True, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/projects', methods=['GET', 'POST'])
def handle_projects():
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json
        cur = conn.cursor()
        cur.execute('INSERT INTO projects (name, description) VALUES (?, ?)', (data['name'], data.get('description', '')))
        conn.commit()
        project_id = cur.lastrowid
        conn.close()
        return jsonify({'id': project_id, 'name': data['name'], 'description': data.get('description')}), 201
    else:
        projects = conn.execute('SELECT * FROM projects').fetchall()
        conn.close()
        return jsonify([dict(p) for p in projects])

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    conn = get_db_connection()
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/projects/<int:project_id>/tasks', methods=['GET', 'POST'])
def handle_tasks(project_id):
    conn = get_db_connection()
    if request.method == 'POST':
        data = request.json
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO tasks (title, description, status, due_date, project_id, assigned_to) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['title'], data.get('description', ''), 'TODO', data.get('due_date'), project_id, data.get('assigned_to')))
        conn.commit()
        task_id = cur.lastrowid
        conn.close()
        return jsonify({'id': task_id}), 201
    else:
        tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,)).fetchall()
        conn.close()
        return jsonify([dict(t) for t in tasks])

@app.route('/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
def update_task(task_id):
    conn = get_db_connection()
    if request.method == 'PUT':
        data = request.json
        conn.execute('UPDATE tasks SET status = ? WHERE id = ?', (data['status'], task_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
