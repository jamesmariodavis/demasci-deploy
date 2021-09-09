from flask import Flask
from app_lib.example_visualization import get_example_html_str

# flask app name in code
app = Flask(__name__)


@app.route("/")
def index() -> str:
    return "Index"


@app.route('/example')
def template() -> str:
    return get_example_html_str()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
