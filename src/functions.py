from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List, Dict, TypedDict, Callable
from icalendar import Calendar, Event
from datetime import datetime, timedelta

class Functions(TypedDict):
    name: str
    description: str
    inputs: List[Dict[str, Dict[str, str]]]
    outputs: List[Dict[str, Dict[str, str]]]
    required: List[str]

    def __init__(self, func):
        super(Functions, self).__init__()
        self.func = func

    def __str__(self):
        inputs = ", ".join(
            [
                f"{name}: {typ}"
                for input in self["inputs"]
                for name, typ in input.items()
            ]
        )
        outputs = ", ".join(
            [
                f"{name}: {typ}"
                for output in self["outputs"]
                for name, typ in output.items()
            ]
        )
        return f"Function Name: {self['name']}\nDescription: {self['description']} \nInputs: {inputs}\nOutputs: {outputs}"

    def to_tool(self):
        properties = {
            name: {"type": typ["type"]}
            for input in self["inputs"]
            for name, typ in input.items()
        }
        return {
            "type": "function",
            "function": {
                "name": self["name"],
                "description": self["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": self["required"],
                },
            },
        }

def insert_event(receiver_email, summary, location, description, timeZone, startTime, endTime):
    try:
        # Step 1: Create the calendar event
        cal = Calendar()
        event = Event()

        event.add('summary', summary)
        event.add('dtstart', datetime(startTime))
        event.add('dtend', datetime(endTime))
        event.add('description', description)
        event.add('location', location)

        cal.add_component(event)

        # Write to .ics file
        with open('event.ics', 'wb') as f:
            f.write(cal.to_ical())

        sender_email = "bglwagent@gmail.com"
        password = "gkkm uuiy gsvk cbil"

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Meeting Invitation"

        # Attach the .ics file
        with open('event.ics', 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename=event.ics')
            msg.attach(part)

        # Add email body
        body = "Please find the attached calendar invite for our meeting."
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print("Email sent successfully!")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            server.quit()
    except Exception as e:
        print(e)
        raise e

def list_events(attendee_email):
    events_result = service.events().list(
        calendarId='primary', q=attendee_email).execute()
    events = events_result.get('items', [])
    return events

def delete_event(event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return {}

# Hardcoded function retrieval for now
def retrieve_functions():
    return [
        Functions(
            name="insert_event",
            description="Create a new event in the personal calendar",
            inputs={
                "receiver_email": {"type": "string"},
                "summary": {"type": "string"},
                "location": {"type": "string"},
                "description": {"type": "string"},
                "timeZone": {"type": "string"},
                "startTime": {"type": "string"},
                "endTime": {"type": "string"},
            },
            outputs={
                "htmlLink": {"type": "string"},
            },
            required=["receiver_email", "summary", "startTime", "endTime"],
        ),
        Functions(
            name="delete_event",
            description="Delete an event after retrieving event ID from listEvents",
            inputs={
                "receiver_email": {"type": "string"},
            },
            outputs={
                "success": {"type": "boolean"}
            },
            required=["receiver_email"],
        ),
    ]


functions_mapping = {
    "insert_event": insert_event,
    "delete_event": delete_event,
}
