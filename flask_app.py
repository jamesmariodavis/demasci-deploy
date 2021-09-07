from flask import Flask, render_template
from markupsafe import escape

# flask app name in code
app = Flask(__name__)


@app.route("/")
def index() -> str:
    return "Index"


@app.route('/hello')
def hello() -> str:
    return 'Hello, World'


@app.route('/user/<string:username>')
def show_user_profile(username: str) -> str:
    return 'User {}'.format(escape(username))


@app.route('/template')
def template() -> str:
    return render_template('list_of_figures.html', figures=['figure1', 'figure2'])


if __name__ == '__main__':
    app.run(host='0.0.0.0')