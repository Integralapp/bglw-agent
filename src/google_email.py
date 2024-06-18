from apiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


def email_thread_to_messages(conversation_id):
    """
    Fetches an email thread using the Google Mail API and returns it in OpenAI message format with "user" and "assistant" roles.

    Args:
        conversation_id: The conversation ID of the email thread.

    Returns:
        A list of dictionaries, where each dictionary represents a message in the thread.
        The dictionary has keys "role" and "content".
    """

    # TODO: Replace with your actual credentials file path (Shrey Bohra can you add the file path here)
    credentials_file = "path/to/your/credentials.json"

    # Define the service scope
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

    # Build the service object
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file, scopes
    )
    http = credentials.authorize(Http())
    service = build("gmail", "v1", http=http)

    # Get message details using conversation ID
    try:
        message = (
            service.users().messages().get(userId="me", id=conversation_id).execute()
        )
    except:
        print(f"Error retrieving message with ID: {conversation_id}")
        return []

    # Extract thread ID from the message
    thread_id = message["threadId"]

    # Get the entire thread using thread ID
    try:
        threads = (
            service.users()
            .threads()
            .list(userId="me", labelIds=["INBOX"], q=f"id:{thread_id}")
            .execute()
        )
    except:
        print(f"Error retrieving thread with ID: {thread_id}")
        return []

    # No messages found in the thread
    if not threads["threads"]:
        return []

    # Process messages and convert to OpenAI format
    messages = []
    for message in threads["threads"][0]["messages"]:
        sender = message["payload"]["headers"][0]["value"]
        content = message["payload"]["parts"][0]["body"]["data"].decode("utf-8")
        # Assign role based on sender email
        if sender.lower() == "jainshreyp@gmail.com":
            role = "assistant"
        else:
            role = "user"
        messages.append({"role": role, "content": content})

    return messages
