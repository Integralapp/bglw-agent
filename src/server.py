from flask import Flask, jsonify
from flask import request
from .google_auth import get_credentials
from googleapiclient.discovery import build
import httplib2
import base64
import json

from .functions import retrieve_functions
from .llm import generate
from .prompt import system_prompt
from .google_email import email_thread_to_messages, create_and_send_response
from .redis_client import RedisClient

app = Flask(__name__)

global_gmail_service = None
current_history_id = None


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

    watch_request = {
        'labelIds': ['INBOX'],
        'topicName': 'projects/email-agent-425404/topics/gmail',
        'labelFilterBehavior': 'INCLUDE'
    }
    res = global_google_service.users().watch(userId='me',
                                              body=watch_request).execute()
    print(res)

    return "<p>Code received and credentials stored!</p>"


@app.route("/get_emails")
def get_emails():
    threads = (global_google_service.users().threads().list(
        userId="me").execute().get("threads", []))
    print(threads)
    conversation_id = "190e0470ee8f1028"
    messages = email_thread_to_messages(conversation_id, global_google_service)
    print(messages)

    return messages


@app.route("/subscription", methods=['POST'])
def process_incoming_webhook():
    try:
        payload = request.get_json()
        message = payload["message"]
        data = message["data"]
        decoded_data = base64.b64decode(data)
        json_data = json.loads(decoded_data)

        history_id = json_data["historyId"]

        global current_history_id
        if current_history_id is None:
            current_history_id = history_id

        # Retrieve history from the given historyId
        history_response = global_google_service.users().history().list(
            userId="me",
            startHistoryId=current_history_id,
            historyTypes=["messageAdded"]).execute()

        current_history_id = history_id

        print("History Response")
        print(history_response)

        # Check if there is history data
        if "history" in history_response:
            history_list = history_response["history"]
        else:
            history_list = []

        # Process history list
        for history in history_list:
            if "messagesAdded" in history:
                for message in history["messagesAdded"]:
                    message_id = message["message"]["id"]
                    RedisClient.enqueue(message_id)
                    # Add to queue

                    # Fetch the message details
                    # message_details = global_google_service.users().messages(
                    # ).get(userId="me", id=message_id).execute()
                    # print(f"New message: {message_details['snippet']}")

        # Retrieve full email thread and transform to OpenAI message format
        # messages = email_thread_to_messages(conversation_id, global_google_service)
        # print(messages)
        return jsonify({'status': 'acknowledged'}, 200)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'acknowledged'}, 200)


def process_message(message_id):
    message_details = global_google_service.users().messages().get(
        userId="me", id=message_id).execute()
    print(f"New message: {message_details['snippet']}")
