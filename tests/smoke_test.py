import os
import sys
import json
# ensure project root is on sys.path so imports find app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import importlib.util
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

        # Add using 'task' field (project form)
        r = client.post('/add', data={'task': 'Project Alpha'}, follow_redirects=True)
        assert r.status_code == 200, 'POST /add (task) failed (status)'

        # Check todos.json content (server should have written items)
        with open(TODOS, 'r') as f:
            items = json.load(f)
        assert 'Test task 1' in items and 'Project Alpha' in items, 'todos.json did not contain added items'

        # Delete first item
        r = client.get('/delete/0', follow_redirects=True)
        assert r.status_code == 200
        with open(TODOS, 'r') as f:
            items = json.load(f)
        assert 'Test task 1' not in items, 'Delete did not remove item'

        # Offline page
        r = client.get('/offline')
        assert r.status_code == 200 and b"You're offline" in r.data or b"offline" in r.data.lower()

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
