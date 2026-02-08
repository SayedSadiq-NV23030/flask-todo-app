from flask import Blueprint, render_template, request, redirect, url_for
import json

todo_routes = Blueprint('todo_routes', __name__)

def load_todos():
    try:
        with open('todos.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_todos(todos):
    with open('todos.json', 'w') as f:
        json.dump(todos, f)

@todo_routes.route('/')
def index():
    todos = load_todos()
    return render_template('index.html', todos=todos)


@todo_routes.route('/add', methods=['POST'])
def add_todo():
    todos = load_todos()
    item = request.form.get('todo') or request.form.get('task')
    if item:
        todos.append(item.strip())
        save_todos(todos)
    return redirect(url_for('todo_routes.index'))


@todo_routes.route('/delete/<int:idx>')
def delete_todo(idx):
    todos = load_todos()
    if 0 <= idx < len(todos):
        todos.pop(idx)
        save_todos(todos)
    return redirect(url_for('todo_routes.index'))
