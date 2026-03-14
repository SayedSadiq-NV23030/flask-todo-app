from flask import Blueprint, jsonify, render_template, request, redirect, url_for
import json
from pathlib import Path

todo_routes = Blueprint('todo_routes', __name__)

TODO_FILE = Path(__file__).resolve().parent.parent / 'todos.json'


def load_todos():
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_todos(todos):
    with open(TODO_FILE, 'w') as f:
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


@todo_routes.route('/update/<int:idx>', methods=['POST'])
def update_todo(idx):
    todos = load_todos()
    item = request.form.get('todo') or request.form.get('task')
    if 0 <= idx < len(todos) and item:
        todos[idx] = item.strip()
        save_todos(todos)
    return redirect(url_for('todo_routes.index'))


@todo_routes.route('/tasks', methods=['GET'])
def list_tasks():
    todos = load_todos()
    tasks = [{'id': idx, 'title': title} for idx, title in enumerate(todos)]
    return jsonify(tasks), 200


@todo_routes.route('/tasks', methods=['POST'])
def create_task():
    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400

    todos = load_todos()
    todos.append(title)
    save_todos(todos)
    return jsonify({'id': len(todos) - 1, 'title': title}), 201


@todo_routes.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400

    todos = load_todos()
    if not (0 <= task_id < len(todos)):
        return jsonify({'error': 'task not found'}), 404

    todos[task_id] = title
    save_todos(todos)
    return jsonify({'id': task_id, 'title': title}), 200


@todo_routes.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    todos = load_todos()
    if not (0 <= task_id < len(todos)):
        return jsonify({'error': 'task not found'}), 404

    deleted = todos.pop(task_id)
    save_todos(todos)
    return jsonify({'deleted': {'id': task_id, 'title': deleted}}), 200


@todo_routes.route('/offline')
def offline():
    return render_template('offline.html')
