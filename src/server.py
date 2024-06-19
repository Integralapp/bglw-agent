from flask import Flask
from flask import request
from .google_auth import get_credentials
from googleapiclient.discovery import build
import httplib2

app = Flask(__name__)

global_gmail_service = None


@app.route("/")
def process_redirect():
    code = request.args.get('code', None)
    if code is None:
        return "<p>No Code provided!</p>"

    credentials = get_credentials(code, "")

    global global_google_service
    global_google_service = build(serviceName="gmail",
                                  version="v1",
                                  http=credentials.authorize(httplib2.Http()))

    return "<p>Code received and credentials stored!</p>"


@app.route("/get_emails")
def get_emails():
    threads = (global_google_service.users().threads().list(
        userId="me").execute().get("threads", []))
    return threads
