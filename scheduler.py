import imaplib
import email
from email.header import decode_header
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from pinecone import Pinecone
import time

# from src.functions import retrieve_functions, functions_mapping
# from src.google_email import create_and_send_response, email_thread_to_messages
from src.llm import _predict_endpoint
from src.prompt import la_prompt_with_retrieval, system_prompt, system_prompt_with_retrieval

# Account credentials
username = "lealfreconcierge@gmail.com"
password = "bwhs olbc vypd zgnp"
imap_server = "imap.gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587  # Usually 587 for TLS
# Function to check for new emails

pc = Pinecone(api_key=os.getenv("PC_API_KEY"))
index = pc.Index("la")

client = OpenAI(
    api_key=os.getenv("OAI_API_KEY")
)

def check_emails():
    try:
        # Connect to the server
        mail = imaplib.IMAP4_SSL(imap_server)
        # Login to your account
        mail.login(username, password)
        # Select the mailbox you want to check
        mail.select("inbox")

        # Search for all new emails (UNSEEN)
        status, messages = mail.search(None, '(UNSEEN)')

        # Convert messages to a list of email IDs
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} new emails")
        emails_list = []

        for email_id in email_ids:
            content = ""
            # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # If it's a bytes, decode to str
                        subject = subject.decode(
                            encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    print("Subject:", subject)
                    print("From:", from_)

                    # If the email message is multipart
                    if msg.is_multipart():
                        for part in msg.walk():
                            # Extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(
                                part.get("Content-Disposition"))

                            try:
                                # Get the email body
                                body = part.get_payload(decode=True).decode()
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    # Print only the email body
                                    print("Body:", body)
                                    content += body
                            except:
                                pass
                    else:
                        # Extract content type of email
                        content_type = msg.get_content_type()

                        # Get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            # Print only the email body
                            print("Body:", body)
                            content += body
                    print(f"EMAIL FROM {from_}: {content}")
                    emails_list.append({
                        "role": "assistant" if from_ == "bglwagent@gmail.com" else "user",
                        "content": f"EMAIL FROM {from_}: {content}"
                    })

                    # Send a response
                    send_response(emails_list, emails_list[-1]["content"], from_, subject)
            print("="*50)
        # Close the connection and logout
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to send a response
        # from dotenv import load_dotenv

        # load_dotenv()

        # # Retrieve functions from a specific API documentation
        # functions = retrieve_functions()

        # # Inject system prompt without functions (passed into Groq directly)
        # prompt = system_prompt(additional_context="")

        # # Retrieve full email thread and transform to OpenAI message format
        # # messages = email_thread_to_messages(conversation_id=conversation_id)

        # # Format the allowed functions to be hit
        # available_functions = functions_mapping

        # # Do recursive function calling on a specific prompt until desired output and functions have been executed

        # print(
        #     [{"role": "system", "content": prompt}, *messages]
        # )
        # generation = generate(
        #     [{"role": "system", "content": prompt}, *messages],
        #     functions,
        #     available_functions=available_functions,
        #     stream=False,
        # )

def send_response(messages, last_message_content, to_email, original_subject):
    try:
        query_embedding = client.embeddings.create(
            input=last_message_content,
            model="text-embedding-3-large"
        ).data[0].embedding

        retrieval = index.query(
            vector=query_embedding,
            top_k=7,
            include_metadata=True,
        )["matches"]

        prompt = la_prompt_with_retrieval(retrieval)

        generation = _predict_endpoint(
            [{"role": "system", "content": prompt}, *messages],
        ).choices[0].message.content

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = username
        msg["To"] = to_email
        msg["Subject"] = f"Re: {original_subject}"

        # Email body
        body = generation
        print("RESPONSE:      ", generation)
        msg.attach(MIMEText(body, "plain"))

        # Connect to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())
        server.quit()
        print(f"Replied to {to_email}")
    except Exception as e:
        print(f"Failed to send response to {to_email}: {e}")
        raise e


# Run the check every minute
while True:
    check_emails()
    time.sleep(10)
