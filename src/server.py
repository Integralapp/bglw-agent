from flask import Flask, jsonify
from flask import request
from google_auth import get_credentials
from googleapiclient.discovery import build
import httplib2
import base64

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
    return threads


@app.route("/subscription", methods=['POST'])
def process_incoming_webhook():
    payload = request.get_json()
    print(payload)
    message = payload["message"]
    message_id = message["messageId"]
    return request.json


# from dotenv import load_dotenv

# load_dotenv()
# # Retrieve conversation ID through API call (from message ID in webhook sig)
# conversation_id = "PLACEHOLDER"

# # Retrieve functions from a specific API documentation
# functions = retrieve_functions()

# # Inject system prompt without functions (passed into Groq directly)
# prompt = system_prompt(additional_context="")

# # Retrieve full email thread and transform to OpenAI message format
# messages = email_thread_to_messages(conversation_id=conversation_id)

# # Format the allowed functions to be hit
# available_functions = {func["name"]: func.func for func in functions}

# # Do recursive function calling on a specific prompt until desired output and functions have been executed
# # TODO: Implement the individual functions on the calendar API
# generation = generate(
#     [{
#         "role": "system",
#         "content": prompt
#     }, *messages],
#     available_functions,
#     stream=False,
# )

# # Add a new message to the thread
# create_and_send_response(generation, thread_id=conversation_id)
