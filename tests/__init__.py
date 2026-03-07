from flask import Flask

app = Flask(__name__)  # This name must match exactly

@app.route('/')
def index():
    return "Hello World"