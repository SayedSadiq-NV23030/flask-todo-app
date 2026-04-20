import os
import sys
import json

# ensure project root is on sys.path so imports find app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import importlib.util  # noqa: E402

app_py = os.path.join(ROOT, 'app.py')
spec = importlib.util.spec_from_file_location('app_main', app_py)
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
flask_app = getattr(app_module, 'app')

TODOS = os.path.join(ROOT, 'todos.json')


def backup_file(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return None


def restore_file(path, content):
    if content is None:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    else:
        with open(path, 'w') as f:
            f.write(content)


def run_smoke():
    orig = backup_file(TODOS)
    try:
        # start with empty todos
        with open(TODOS, 'w') as f:
            json.dump([], f)

        client = flask_app.test_client()

        r = client.get('/')
        assert r.status_code == 200, 'GET / failed'

        # Add using 'todo' field (server-side storage)
        r = client.post('/add', data={'todo': 'Test task 1'}, follow_redirects=True)
        assert r.status_code == 200, 'POST /add (todo) failed (status)'

        # Add using 'task' field + metadata
        r = client.post('/add', data={
            'task': 'Project Alpha',
            'description': 'Milestone preparation',
            'priority': '1',
            'due_date': '2099-12-31'
        }, follow_redirects=True)
        assert r.status_code == 200, 'POST /add (task) failed (status)'

        # Check todos.json content (server should have written structured items)
        with open(TODOS, 'r') as f:
            items = json.load(f)
        titles = [i.get('title') for i in items]
        assert 'Test task 1' in titles and 'Project Alpha' in titles, 'todos.json missing expected titles'
        alpha = next(i for i in items if i.get('title') == 'Project Alpha')
        assert alpha.get('description') == 'Milestone preparation'
        assert alpha.get('priority') == 1
        assert alpha.get('due_date') == '2099-12-31'
        assert alpha.get('status') == 'active'

        # Delete first item
        r = client.get('/delete/0', follow_redirects=True)
        assert r.status_code == 200
        with open(TODOS, 'r') as f:
            items = json.load(f)
        titles_after_delete = [i.get('title') for i in items]
        assert 'Project Alpha' not in titles_after_delete, 'Delete did not remove item'

        # API: search by title/description
        r = client.get('/api/tasks?q=test')
        assert r.status_code == 200
        payload = r.get_json()
        assert payload['count'] == 1
        assert payload['tasks'][0]['title'] == 'Test task 1'

        # API: create then filter by completed status
        r = client.post('/api/tasks', json={
            'title': 'API Task',
            'description': 'Created from test',
            'priority': 3,
            'due_date': '2099-10-01',
            'tags': 'ops,backend'
        })
        assert r.status_code == 201
        created = r.get_json()
        r = client.patch(f"/api/tasks/{created['id']}", json={'status': 'completed'})
        assert r.status_code == 200

        r = client.get('/api/tasks?status=completed&sort=priority&order=asc')
        assert r.status_code == 200
        payload = r.get_json()
        assert any(t['id'] == created['id'] for t in payload['tasks'])

        # API: tags listing and filtering
        r = client.get('/api/tags')
        assert r.status_code == 200
        tags_payload = r.get_json()
        assert any(t.lower() == 'ops' for t in tags_payload['tags'])

        r = client.get('/api/tasks?tag=ops')
        assert r.status_code == 200
        payload = r.get_json()
        assert any(t['id'] == created['id'] for t in payload['tasks'])

        # API: stats dashboard
        r = client.get('/api/stats')
        assert r.status_code == 200
        stats_payload = r.get_json()
        assert stats_payload.get('total_tasks', 0) >= 1
        assert stats_payload.get('completed_tasks', 0) >= 1

        # Offline page
        r = client.get('/offline')
        assert r.status_code == 200 and (
            b"You're offline" in r.data or b"offline" in r.data.lower()
        )

        # Manifest and static assets
        r = client.get('/static/manifest.json')
        assert r.status_code == 200
        manifest = json.loads(r.data)
        assert manifest.get('name'), 'Manifest missing name'

        print('SMOKE TESTS PASSED')

    finally:
        restore_file(TODOS, orig)


if __name__ == '__main__':
    run_smoke()
