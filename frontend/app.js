const API_URL = '';

let currentUser = null;
let currentProject = null;
let allUsers = [];

window.onload = function() {
    const savedUser = localStorage.getItem('taskMasterUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
    }

    const isLoginPage = document.getElementById('login-form') !== null;
    if (isLoginPage && currentUser) window.location.href = 'dashboard.html';
    else if (!isLoginPage && !currentUser) window.location.href = 'index.html';

    if (isLoginPage) setupLogin();
    else setupDashboard();
};

function setupLogin() {
    const form = document.getElementById('login-form');
    form.onsubmit = function(event) {
        event.preventDefault();
        const usernameInput = document.getElementById('username').value;
        const passwordInput = document.getElementById('password').value;

        fetch(API_URL + '/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: usernameInput, password: passwordInput })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                localStorage.setItem('taskMasterUser', JSON.stringify(data.user));
                window.location.href = 'dashboard.html';
            } else {
                document.getElementById('login-error').innerText = data.message;
            }
        })
        .catch(function(err) {
            document.getElementById('login-error').innerText = 'Error connecting to server.';
        });
    };
}

function setupDashboard() {
    document.getElementById('current-user-name').innerText = currentUser.username;
    document.getElementById('current-user-role').innerText = currentUser.role.toUpperCase();

    if (currentUser.role === 'admin') {
        const adminEls = document.querySelectorAll('.admin-only');
        for (let i = 0; i < adminEls.length; i++) adminEls[i].style.display = 'block';
    }

    document.getElementById('logout-btn').onclick = function() {
        localStorage.removeItem('taskMasterUser');
        window.location.href = 'index.html';
    };

    document.getElementById('back-to-projects').onclick = function() {
        document.getElementById('tasks-view').style.display = 'none';
        document.getElementById('projects-view').style.display = 'block';
    };

    setupModals();
    loadProjects();
    loadUsers();
}

function setupModals() {
    // Project Modal
    const showProjectBtn = document.getElementById('show-project-form-btn');
    if (showProjectBtn) {
        showProjectBtn.onclick = function() {
            document.getElementById('project-modal').style.display = 'flex';
        };
    }
    
    // Task Modal
    const showTaskBtn = document.getElementById('show-task-form-btn');
    if (showTaskBtn) {
        showTaskBtn.onclick = function() {
            document.getElementById('task-modal').style.display = 'flex';
        };
    }

    // Close Modals
    const closeBtns = document.querySelectorAll('.close-modal');
    for (let i = 0; i < closeBtns.length; i++) {
        closeBtns[i].onclick = function() {
            const modalId = this.getAttribute('data-modal');
            document.getElementById(modalId).style.display = 'none';
        };
    }

    // Submit Project
    document.getElementById('project-form').onsubmit = function(event) {
        event.preventDefault();
        const name = document.getElementById('project-name').value;
        const desc = document.getElementById('project-desc').value;

        fetch(API_URL + '/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, description: desc })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            document.getElementById('project-form').reset();
            document.getElementById('project-modal').style.display = 'none';
            loadProjects();
        });
    };

    // Submit Task
    document.getElementById('task-form').onsubmit = function(event) {
        event.preventDefault();
        const title = document.getElementById('task-title').value;
        const desc = document.getElementById('task-desc').value;
        const assigned = document.getElementById('task-assignee').value;
        const dueDate = document.getElementById('task-due-date').value;

        fetch(API_URL + '/projects/' + currentProject.id + '/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, description: desc, assigned_to: assigned, due_date: dueDate })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            document.getElementById('task-form').reset();
            document.getElementById('task-modal').style.display = 'none';
            loadTasks();
        });
    };
}

function loadProjects() {
    fetch(API_URL + '/projects')
        .then(function(res) { return res.json(); })
        .then(function(projects) {
            const list = document.getElementById('projects-list');
            list.innerHTML = '';
            
            for (let i = 0; i < projects.length; i++) {
                let p = projects[i];
                let card = document.createElement('div');
                card.className = 'project-card';
                card.innerHTML = '<h3>' + p.name + '</h3><p>' + (p.description || '') + '</p>';
                card.onclick = function() { openProject(p); };
                
                if (currentUser.role === 'admin') {
                    let delBtn = document.createElement('button');
                    delBtn.className = 'btn btn-sm btn-danger delete-project-btn';
                    delBtn.innerHTML = 'Delete &times;';
                    delBtn.onclick = function(e) {
                        e.stopPropagation();
                        deleteProject(p.id);
                    };
                    card.appendChild(delBtn);
                }

                list.appendChild(card);
            }
        });
}

function deleteProject(pid) {
    if(confirm("Are you sure you want to delete this project and all its tasks?")) {
        fetch(API_URL + '/projects/' + pid, { method: 'DELETE' })
            .then(function() { loadProjects(); });
    }
}

function loadUsers() {
    fetch(API_URL + '/users')
        .then(function(res) { return res.json(); })
        .then(function(users) {
            allUsers = users;
            const select = document.getElementById('task-assignee');
            for (let i = 0; i < users.length; i++) {
                let u = users[i];
                let opt = document.createElement('option');
                opt.value = u.id;
                opt.innerText = u.username;
                select.appendChild(opt);
            }
        });
}

function openProject(project) {
    currentProject = project;
    document.getElementById('projects-view').style.display = 'none';
    document.getElementById('tasks-view').style.display = 'block';
    document.getElementById('current-project-title').innerText = project.name;
    loadTasks();
}

function loadTasks() {
    fetch(API_URL + '/projects/' + currentProject.id + '/tasks')
        .then(function(res) { return res.json(); })
        .then(function(tasks) {
            document.getElementById('list-TODO').innerHTML = '';
            document.getElementById('list-IN_PROGRESS').innerHTML = '';
            document.getElementById('list-DONE').innerHTML = '';

            for (let i = 0; i < tasks.length; i++) {
                let t = tasks[i];
                
                let assigneeName = 'Unassigned';
                for (let j = 0; j < allUsers.length; j++) {
                    if (allUsers[j].id === t.assigned_to) {
                        assigneeName = allUsers[j].username;
                    }
                }

                let card = document.createElement('div');
                card.className = 'task-card';
                
                let statusHtml = '<select class="form-control-sm" onchange="changeTaskStatus(' + t.id + ', this.value)">';
                statusHtml += '<option value="TODO" ' + (t.status === 'TODO' ? 'selected' : '') + '>TODO</option>';
                statusHtml += '<option value="IN_PROGRESS" ' + (t.status === 'IN_PROGRESS' ? 'selected' : '') + '>In Progress</option>';
                statusHtml += '<option value="DONE" ' + (t.status === 'DONE' ? 'selected' : '') + '>Done</option>';
                statusHtml += '</select>';

                let deleteBtnHtml = '';
                if (currentUser.role === 'admin') {
                    deleteBtnHtml = '<button class="btn btn-sm btn-danger" onclick="deleteTask(' + t.id + ')">Delete</button>';
                }

                let dueDateHtml = t.due_date ? '<span class="due-date">Due: ' + t.due_date + '</span>' : '<span>No Date</span>';

                card.innerHTML = '<h4>' + t.title + '</h4>' +
                               '<div class="task-desc">' + t.description + '</div>' +
                               '<div class="task-meta">' +
                               '   <span>👤 ' + assigneeName + '</span>' + dueDateHtml + 
                               '</div>' +
                               '<div class="task-controls">' + statusHtml + deleteBtnHtml + '</div>';
                
                let containerId = 'list-' + t.status;
                let container = document.getElementById(containerId);
                if (container) container.appendChild(card);
            }
        });
}

window.changeTaskStatus = function(taskId, newStatus) {
    fetch(API_URL + '/tasks/' + taskId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    }).then(function(res) { loadTasks(); });
};

window.deleteTask = function(taskId) {
    if (confirm('Delete this task?')) {
        fetch(API_URL + '/tasks/' + taskId, { method: 'DELETE' })
            .then(function(res) { loadTasks(); });
    }
};
