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
    return render_template('index.html', todos=todos)  # Ensure this is correct
