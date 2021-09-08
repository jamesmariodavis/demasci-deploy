from flask import Flask
from markupsafe import escape
from app_lib import JinjaRender

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
    return JinjaRender.render_template(
        template_name=JinjaRender.LIST_OF_FIGURES_TEMPLATE,
        params={'figures': ['a', 'b']},
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
