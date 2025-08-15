from app import app
from flask import current_app
@app.route('/')
@app.route('/index')
def index():
    return "<h1>Hello, Flask!</h1>"
@app.route('/appname')
def appname():
    name = current_app.name
    return '<p> Ihre App heisst: {}</p>'.format(name)