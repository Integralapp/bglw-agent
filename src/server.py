from flask import Flask
from flask import request
from src.google_auth import get_credentials

app = Flask(__name__)


@app.route("/")
def hello_world():
    code = request.args.get('code')
    print(code)

    credentials = get_credentials(code, "")
    print(credentials)

    return "<p>Hello, World!</p>"
