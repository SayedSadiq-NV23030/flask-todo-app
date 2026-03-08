import importlib.util
import os


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
