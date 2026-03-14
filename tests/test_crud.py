import importlib.util
import json
import os

import pytest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_PY = os.path.join(ROOT, 'app.py')
TODOS = os.path.join(ROOT, 'todos.json')


spec = importlib.util.spec_from_file_location('app_main', APP_PY)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
flask_app = app_module.app


def _backup_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None


def _restore_file(path, content):
    if content is None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    else:
        with open(path, 'w') as f:
            f.write(content)


@pytest.fixture
def client():
    original = _backup_file(TODOS)
    with open(TODOS, 'w') as f:
        json.dump([], f)

    flask_app.config['TESTING'] = True
    with flask_app.test_client() as test_client:
        yield test_client

    _restore_file(TODOS, original)


def test_create_task(client):
    # Arrange + Act: create a task via JSON API
    resp = client.post('/tasks', json={'title': 'Buy milk'})

    # Assert: status and payload
    assert resp.status_code == 201
    created = resp.get_json()
    assert created['title'] == 'Buy milk'

    # Read/verify list contains new task
    listed = client.get('/tasks')
    assert listed.status_code == 200
    titles = [task['title'] for task in listed.get_json()]
    assert 'Buy milk' in titles


def test_update_task(client):
    # Arrange: create an initial task
    created = client.post('/tasks', json={'title': 'Old title'})
    assert created.status_code == 201
    task_id = created.get_json()['id']

    # Act: update the task
    updated = client.put(f'/tasks/{task_id}', json={'title': 'New title'})

    # Assert: status and updated content
    assert updated.status_code == 200
    assert updated.get_json()['title'] == 'New title'

    # Read/verify list reflects update
    listed = client.get('/tasks')
    assert listed.status_code == 200
    titles = [task['title'] for task in listed.get_json()]
    assert 'New title' in titles
    assert 'Old title' not in titles


def test_delete_task(client):
    # Arrange: create a task to delete
    created = client.post('/tasks', json={'title': 'To be deleted'})
    assert created.status_code == 201
    task_id = created.get_json()['id']

    # Act: delete task
    deleted = client.delete(f'/tasks/{task_id}')

    # Assert: status and delete payload
    assert deleted.status_code == 200
    assert deleted.get_json()['deleted']['title'] == 'To be deleted'

    # Read/verify list no longer contains task
    listed = client.get('/tasks')
    assert listed.status_code == 200
    titles = [task['title'] for task in listed.get_json()]
    assert 'To be deleted' not in titles
