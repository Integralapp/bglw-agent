import imaplib

imap_ssl_host = 'imap.gmail.com'
imap_ssl_port = 993


def check_for_emails():
  from config import EMAIL, PASSWORD

  email = EMAIL
  password = PASSWORD
  
  try:
    # Connect to the IMAP server
    imap = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    print(email, password)
    imap.login(email, password)

    # Select the inbox folder
    imap.select("inbox")

    # Search for unseen emails
    status, data = imap.search(None, "UNSEEN")

    print(data)
    unseen_emails = data[0].split()  # Split string of email IDs

    # Process unseen emails (replace with your desired actions)
    if unseen_emails:
      for email_id in unseen_emails:
        print(f"Found new email: {email_id}")
        # You can fetch the email content here using imap.fetch()

    # Close the connection
    imap.close()
    imap.logout()

  except Exception as e:
    print(f"An error occurred: {e}")