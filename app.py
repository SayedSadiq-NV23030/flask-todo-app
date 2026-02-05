from flask import Flask
from app.routes import todo_routes
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'app/templates'))
app.register_blueprint(todo_routes)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
