# Team Task Management Application

A full-stack web application designed for teams to efficiently manage projects, track tasks, and collaborate. Built with a focus on simplicity, readability, and clean architecture without relying on heavy frontend frameworks.

## Features

- **User Authentication**: Secure login system with role-based access control.
- **Role Management**:
  - **Admin**: Can create/delete projects, manage all tasks, and assign work to members.
  - **Member**: Can view assigned projects, update task statuses, and track team progress.
- **Project Dashboard**: Organize work into dedicated projects.
- **Task Tracking**: Create tasks with titles, descriptions, assignees, and due dates. Move tasks across `TODO`, `In Progress`, and `Done` states.
- **Responsive UI**: A modern, clean interface built with vanilla CSS.

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite (Local Development) / PostgreSQL (Production)
- **Frontend**: HTML5, Vanilla JavaScript (ES6), CSS3

## Local Setup

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd team-task-manager
   ```

2. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```
   The backend handles database initialization automatically on the first run.

4. Open your browser and navigate to `http://localhost:5000/`.

## Default Credentials
For demonstration purposes, the database automatically seeds the following users:
- **Admin**: `admin` / `admin123`
- **Member**: `member` / `member123`

## Deployment

This application is configured for deployment on Render via a `render.yaml` Blueprint.

1. Create a [Render](https://render.com/) account.
2. Click **New +** > **Blueprint**.
3. Connect this repository. Render will automatically provision a free PostgreSQL database and deploy the Flask web service.

## Architecture & Code Quality
This project was developed with a strong emphasis on clean code and maintainability. The frontend relies on vanilla JavaScript to demonstrate core DOM manipulation and API integration skills without the overhead of heavy frameworks like React or Vue. The backend follows RESTful principles using Flask and SQLAlchemy for robust ORM-based database operations.
