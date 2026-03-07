import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_app_import():
    """Test that the app imports successfully."""
    assert app is not None
    assert app.config['DEBUG'] is False


def test_index_route(client):
    """Test GET / returns 200 and contains HTML."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


def test_board_route(client):
    """Test GET /board returns 200 and contains board HTML."""
    response = client.get('/board')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


def test_create_task(client):
    """Test POST /tasks creates a task and returns 201."""
    payload = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high",
    }
    response = client.post('/tasks', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['task'] == payload


def test_get_task(client):
    """Test GET /tasks/<task_id> returns task data."""
    response = client.get('/tasks/test-task-1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['taskId'] == 'test-task-1'


def test_update_task(client):
    """Test PUT /tasks/<task_id> updates a task."""
    payload = {"title": "Updated Task", "status": "completed"}
    response = client.put('/tasks/test-task-1', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['taskId'] == 'test-task-1'
    assert data['task'] == payload


def test_delete_task(client):
    """Test DELETE /tasks/<task_id> deletes a task."""
    response = client.delete('/tasks/test-task-1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['taskId'] == 'test-task-1'


def test_progress_route(client):
    """Test GET /progress returns progress data."""
    response = client.get('/progress')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'progress' in data