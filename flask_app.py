from flask import Flask
from markupsafe import escape
from app_lib.example_visualization import get_example_html_str

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


@app.route('/example_plot')
def template() -> str:
    return get_example_html_str()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
