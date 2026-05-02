import os
from sqlalchemy import create_engine, text

# Handle Render's DATABASE_URL which starts with postgres:// instead of postgresql://
db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database.db')}")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

def get_db_connection():
    return engine.connect()

def init_db():
    with get_db_connection() as conn:
        pk_type = "SERIAL PRIMARY KEY" if engine.name == "postgresql" else "INTEGER PRIMARY KEY AUTOINCREMENT"
        
        conn.execute(text(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'member'
            )
        '''))
        conn.execute(text(f'''
            CREATE TABLE IF NOT EXISTS projects (
                id {pk_type},
                name TEXT NOT NULL,
                description TEXT
            )
        '''))
        conn.execute(text(f'''
            CREATE TABLE IF NOT EXISTS tasks (
                id {pk_type},
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'TODO',
                due_date TEXT,
                project_id INTEGER,
                assigned_to INTEGER,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(assigned_to) REFERENCES users(id)
            )
        '''))
        
        result = conn.execute(text('SELECT COUNT(*) FROM users'))
        if result.scalar() == 0:
            conn.execute(text("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')"))
            conn.execute(text("INSERT INTO users (username, password, role) VALUES ('member', 'member123', 'member')"))

        conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
