import importlib.util
import os
import json


def load_flask_app():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app_py = os.path.join(root, 'app.py')
    spec = importlib.util.spec_from_file_location('app_main', app_py)
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    return app_module.app


def test_app_import():
    app = load_flask_app()

    assert app is not None


def test_app_responds():
    app = load_flask_app()

    app.config['TESTING'] = True
    with app.test_client() as client:
        response = client.get('/')

    assert response.status_code in [200, 302]


def test_api_task_lifecycle(tmp_path):
    app = load_flask_app()
    app.config['TESTING'] = True

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with open('todos.json', 'w') as f:
            json.dump([], f)

        with app.test_client() as client:
            create = client.post('/api/tasks', json={
                'title': 'Test API task',
                'description': 'Find this by query',
                'priority': 1,
                'due_date': '2099-01-01'
            })
            assert create.status_code == 201
            task = create.get_json()

            search = client.get('/api/tasks?q=find')
            assert search.status_code == 200
            payload = search.get_json()
            assert payload['count'] == 1
            assert payload['tasks'][0]['id'] == task['id']

            update = client.patch(f"/api/tasks/{task['id']}", json={'status': 'completed'})
            assert update.status_code == 200
            assert update.get_json()['status'] == 'completed'

            completed = client.get('/api/tasks?status=completed')
            assert completed.status_code == 200
            payload = completed.get_json()
            assert any(t['id'] == task['id'] for t in payload['tasks'])
    finally:
        os.chdir(cwd)


def test_tags_and_stats_endpoints(tmp_path):
    app = load_flask_app()
    app.config['TESTING'] = True

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with open('todos.json', 'w') as f:
            json.dump([], f)

        with app.test_client() as client:
            create = client.post('/api/tasks', json={
                'title': 'Tagged task',
                'description': 'Has labels',
                'priority': 2,
                'tags': 'work,urgent'
            })
            assert create.status_code == 201
            task = create.get_json()

            tags = client.get('/api/tags')
            assert tags.status_code == 200
            tags_payload = tags.get_json()
            assert 'work' in [t.lower() for t in tags_payload['tags']]

            by_tag = client.get('/api/tasks?tag=work')
            assert by_tag.status_code == 200
            by_tag_payload = by_tag.get_json()
            assert any(t['id'] == task['id'] for t in by_tag_payload['tasks'])

            client.patch(f"/api/tasks/{task['id']}", json={'status': 'completed'})
            stats = client.get('/api/stats')
            assert stats.status_code == 200
            stats_payload = stats.get_json()
            assert stats_payload['total_tasks'] == 1
            assert stats_payload['completed_tasks'] == 1
    finally:
        os.chdir(cwd)


def test_subtasks_lifecycle(tmp_path):
    app = load_flask_app()
    app.config['TESTING'] = True

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        with open('todos.json', 'w') as f:
            json.dump([], f)

        with app.test_client() as client:
            create_task = client.post('/api/tasks', json={'title': 'Parent task'})
            assert create_task.status_code == 201
            task = create_task.get_json()

            s1 = client.post(f"/api/tasks/{task['id']}/subtasks", json={'title': 'First step'})
            s2 = client.post(f"/api/tasks/{task['id']}/subtasks", json={'title': 'Second step'})
            assert s1.status_code == 201
            assert s2.status_code == 201
            sub1 = s1.get_json()
            sub2 = s2.get_json()

            toggle = client.patch(f"/api/tasks/{task['id']}/subtasks/{sub1['id']}", json={'is_done': True})
            assert toggle.status_code == 200
            assert toggle.get_json()['is_done'] is True

            reorder = client.post(
                f"/api/tasks/{task['id']}/subtasks/reorder",
                json={'ordered_ids': [sub2['id'], sub1['id']]},
            )
            assert reorder.status_code == 200
            reordered = reorder.get_json()['subtasks']
            assert reordered[0]['id'] == sub2['id']

            remove = client.delete(f"/api/tasks/{task['id']}/subtasks/{sub2['id']}")
            assert remove.status_code == 200
    finally:
        os.chdir(cwd)
