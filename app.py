from flask import Flask
from app.routes import todo_routes
import os

# Configure template and static folders to match project layout
template_dir = os.path.join(os.path.dirname(__file__), 'app/templates')
static_dir = os.path.join(os.path.dirname(__file__), 'app/static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, static_url_path='/static')
app.register_blueprint(todo_routes)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
