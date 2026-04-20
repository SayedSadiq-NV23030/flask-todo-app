from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import json
import uuid
from datetime import date, datetime, timedelta, timezone

todo_routes = Blueprint('todo_routes', __name__)

TODO_FILE = 'todos.json'
PRIORITY_LEVELS = {1, 2, 3}
STATUS_VALUES = {'active', 'completed'}


def load_todos():
    try:
        with open(TODO_FILE, 'r') as f:
            raw = json.load(f)
    except FileNotFoundError:
        return []

    normalized = []
    for item in raw:
        normalized.append(normalize_task(item))

    # Backfill older formats (plain strings / partial dicts) to full task records.
    if normalized != raw:
        save_todos(normalized)

    return normalized


def save_todos(todos):
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=2)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_due_date(value):
    if not value:
        return ''
    try:
        return datetime.strptime(value, '%Y-%m-%d').date().isoformat()
    except ValueError:
        return ''


def normalize_priority(priority):
    try:
        parsed = int(priority)
    except (TypeError, ValueError):
        parsed = 2
    return parsed if parsed in PRIORITY_LEVELS else 2


def normalize_status(status, done=None):
    if status in STATUS_VALUES:
        return status
    if isinstance(done, bool):
        return 'completed' if done else 'active'
    return 'active'


def normalize_task(item):
    timestamp = now_iso()

    if isinstance(item, str):
        return {
            'id': uuid.uuid4().hex,
            'title': item.strip(),
            'description': '',
            'priority': 2,
            'due_date': '',
            'status': 'active',
            'created_at': timestamp,
            'updated_at': timestamp,
        }

    if not isinstance(item, dict):
        return {
            'id': uuid.uuid4().hex,
            'title': str(item),
            'description': '',
            'priority': 2,
            'due_date': '',
            'status': 'active',
            'created_at': timestamp,
            'updated_at': timestamp,
        }

    title = str(item.get('title') or item.get('todo') or item.get('task') or '').strip()
    if not title:
        title = 'Untitled Task'

    created_at = item.get('created_at') or item.get('createdAt') or timestamp
    updated_at = item.get('updated_at') or created_at
    normalized = {
        'id': str(item.get('id') or uuid.uuid4().hex),
        'title': title,
        'description': str(item.get('description') or '').strip(),
        'priority': normalize_priority(item.get('priority')),
        'due_date': parse_due_date(item.get('due_date')),
        'status': normalize_status(item.get('status'), item.get('done')),
        'created_at': created_at,
        'updated_at': updated_at,
    }
    return normalized


def due_bucket(task, bucket):
    due_date = parse_due_date(task.get('due_date'))
    if not due_date:
        return False

    due = datetime.strptime(due_date, '%Y-%m-%d').date()
    today = date.today()

    if bucket == 'overdue':
        return due < today
    if bucket == 'today':
        return due == today
    if bucket == 'this_week':
        end_of_week = today + timedelta(days=(6 - today.weekday()))
        return today <= due <= end_of_week
    return True


def sort_tasks(tasks, sort_by, order):
    reverse = order == 'desc'

    def due_sort_value(task):
        due = parse_due_date(task.get('due_date'))
        return due or '9999-12-31'

    if sort_by == 'due_date':
        return sorted(tasks, key=due_sort_value, reverse=reverse)
    if sort_by == 'priority':
        return sorted(tasks, key=lambda t: int(t.get('priority') or 2), reverse=reverse)
    if sort_by == 'title':
        return sorted(tasks, key=lambda t: (t.get('title') or '').lower(), reverse=reverse)
    return sorted(tasks, key=lambda t: t.get('created_at') or '', reverse=reverse)


def query_tasks(todos):
    q = (request.args.get('q') or '').strip().lower()
    status = (request.args.get('status') or 'all').strip().lower()
    priority = (request.args.get('priority') or '').strip()
    due = (request.args.get('due') or '').strip().lower()
    sort_by = (request.args.get('sort') or 'created_at').strip().lower()
    order = (request.args.get('order') or 'desc').strip().lower()

    filtered = todos
    if q:
        filtered = [
            task for task in filtered
            if q in task['title'].lower() or q in task.get('description', '').lower()
        ]

    if status in STATUS_VALUES:
        filtered = [task for task in filtered if task.get('status') == status]

    if priority:
        try:
            wanted_priority = int(priority)
            filtered = [task for task in filtered if task.get('priority') == wanted_priority]
        except ValueError:
            pass

    if due in {'overdue', 'today', 'this_week'}:
        filtered = [task for task in filtered if due_bucket(task, due)]

    if sort_by not in {'created_at', 'due_date', 'priority', 'title'}:
        sort_by = 'created_at'
    if order not in {'asc', 'desc'}:
        order = 'desc'

    return sort_tasks(filtered, sort_by, order)


def build_task_from_request(payload):
    title = (payload.get('title') or payload.get('todo') or payload.get('task') or '').strip()
    if not title:
        return None

    timestamp = now_iso()
    return {
        'id': uuid.uuid4().hex,
        'title': title,
        'description': (payload.get('description') or '').strip(),
        'priority': normalize_priority(payload.get('priority')),
        'due_date': parse_due_date(payload.get('due_date')),
        'status': normalize_status(payload.get('status')),
        'created_at': timestamp,
        'updated_at': timestamp,
    }


@todo_routes.route('/')
def index():
    return render_template('index.html')


@todo_routes.route('/add', methods=['POST'])
def add_todo():
    todos = load_todos()
    task = build_task_from_request(request.form)
    if task:
        todos.insert(0, task)
        save_todos(todos)
    return redirect(url_for('todo_routes.index'))


@todo_routes.route('/delete/<int:idx>')
def delete_todo(idx):
    todos = load_todos()
    if 0 <= idx < len(todos):
        todos.pop(idx)
        save_todos(todos)
    return redirect(url_for('todo_routes.index'))


@todo_routes.route('/api/tasks', methods=['GET'])
def get_tasks():
    todos = load_todos()
    filtered = query_tasks(todos)
    return jsonify({'tasks': filtered, 'count': len(filtered)})


@todo_routes.route('/api/tasks', methods=['POST'])
def create_task():
    todos = load_todos()
    payload = request.get_json(silent=True) or request.form
    task = build_task_from_request(payload)
    if not task:
        return jsonify({'error': 'title is required'}), 400

    todos.insert(0, task)
    save_todos(todos)
    return jsonify(task), 201


@todo_routes.route('/api/tasks/<task_id>', methods=['PATCH'])
def update_task(task_id):
    todos = load_todos()
    payload = request.get_json(silent=True) or {}
    updated = None

    for task in todos:
        if task.get('id') != task_id:
            continue

        if 'title' in payload and str(payload.get('title', '')).strip():
            task['title'] = str(payload.get('title')).strip()
        if 'description' in payload:
            task['description'] = str(payload.get('description') or '').strip()
        if 'priority' in payload:
            task['priority'] = normalize_priority(payload.get('priority'))
        if 'due_date' in payload:
            task['due_date'] = parse_due_date(payload.get('due_date'))
        if 'status' in payload:
            task['status'] = normalize_status(payload.get('status'))

        task['updated_at'] = now_iso()
        updated = task
        break

    if not updated:
        return jsonify({'error': 'task not found'}), 404

    save_todos(todos)
    return jsonify(updated)


@todo_routes.route('/api/tasks/<task_id>', methods=['DELETE'])
def remove_task(task_id):
    todos = load_todos()
    kept = [task for task in todos if task.get('id') != task_id]
    if len(kept) == len(todos):
        return jsonify({'error': 'task not found'}), 404

    save_todos(kept)
    return jsonify({'ok': True})


@todo_routes.route('/tasks', methods=['GET'])
def list_tasks_legacy():
    todos = load_todos()
    return jsonify([{'id': task.get('id'), 'title': task.get('title')} for task in todos]), 200


@todo_routes.route('/tasks', methods=['POST'])
def create_task_legacy():
    payload = request.get_json(silent=True) or {}
    task = build_task_from_request(payload)
    if not task:
        return jsonify({'error': 'title is required'}), 400

    todos = load_todos()
    todos.append(task)
    save_todos(todos)
    return jsonify({'id': task['id'], 'title': task['title']}), 201


@todo_routes.route('/tasks/<task_id>', methods=['PUT'])
def update_task_legacy(task_id):
    payload = request.get_json(silent=True) or {}
    title = str(payload.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'title is required'}), 400

    todos = load_todos()
    updated = None
    for task in todos:
        if task.get('id') != task_id:
            continue
        task['title'] = title
        task['updated_at'] = now_iso()
        updated = task
        break

    if not updated:
        return jsonify({'error': 'task not found'}), 404

    save_todos(todos)
    return jsonify({'id': updated['id'], 'title': updated['title']}), 200


@todo_routes.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task_legacy(task_id):
    todos = load_todos()
    deleted = None
    kept = []
    for task in todos:
        if task.get('id') == task_id and deleted is None:
            deleted = task
            continue
        kept.append(task)

    if not deleted:
        return jsonify({'error': 'task not found'}), 404

    save_todos(kept)
    return jsonify({'deleted': {'id': deleted['id'], 'title': deleted['title']}}), 200


@todo_routes.route('/offline')
def offline():
    return render_template('offline.html')
