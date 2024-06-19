from flask import Flask
from flask import request
from flask import session

app = Flask(__name__)


@app.route("/")
def hello_world():
    code = request.args.get('code')
    print(code)
    
    
    
    return "<p>Hello, World!</p>"
