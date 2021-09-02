from flask import Flask
from markupsafe import escape

# flask app name in code
app = Flask(__name__)


@app.route("/")
def index():
    return "Index"


@app.route('/hello')
def hello():
    return 'Hello, World'


@app.route('/user/<string:username>')
def show_user_profile(username: str):
    return 'User {}'.format(escape(username))


if __name__ == '__main__':
    app.run(host='0.0.0.0')