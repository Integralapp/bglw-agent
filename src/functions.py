from typing import List, Dict, TypedDict, Callable
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials from the credentials.json file
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'path/to/credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=credentials)


class Functions(TypedDict):
    name: str
    description: str
    inputs: List[Dict[str, Dict[str, str]]]
    outputs: List[Dict[str, Dict[str, str]]]
    required: List[str]
    func: Callable

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

def insert_event(summary, location, description, timeZone, startTime, endTime):
    event_data = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": startTime,
            "timeZone": timeZone,
        },
        "end": {
            "dateTime": endTime,
            "timeZone": timeZone,
        }
    }
    event = service.events().insert(calendarId='primary', body=event_data).execute()
    return {"htmlLink": event.get("htmlLink")}

def list_events(attendee_email):
    events_result = service.events().list(
        calendarId='primary', q=attendee_email).execute()
    events = events_result.get('items', [])
    return events

def edit_event(event_id, additional_guests, end_date, end_datetime, location, start_date, start_datetime, summary):
    event_data = {
        "summary": summary,
        "location": location,
        "start": {
            "dateTime": start_datetime,
            "timeZone": "EST",  # Adjust as needed
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "EST",  # Adjust as needed
        },
        "attendees": [
            {"email": email} for email in additional_guests.split(',')
        ]
    }
    event = service.events().update(calendarId='primary',
                                    eventId=event_id, body=event_data).execute()
    return event

def delete_event(event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return {}

# Hardcoded function retrieval for now
def retrieve_functions():
    return [
        Functions(
            name="insertEvent",
            description="Create a new event in the personal calendar",
            inputs={
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
            required=["summary", "startTime", "endTime"],
            func=insert_event,
        ),
        Functions(
            name="listEvents",
            description="Retrieve a single event given the attendee email",
            inputs={
                "attendee_email": {"type": "string"},
            },
            outputs={
                "id": {"type": "string"},
                "summary": {"type": "string"},
                "location": {"type": "string"},
                "description": {"type": "string"},
                "timeZone": {"type": "string"},
                "startTime": {"type": "string"},
                "endTime": {"type": "string"},
            },
            required=["attendee_email"],
            func=list_events,
        ),
        Functions(
            name="editEvent",
            description="Edit event by ID after retrieving event ID from listEvents",
            inputs={
                "event_id": {"type": "string"},
                "additional_guests": {"type": "string"},
                "end_date": {"type": "string"},
                "end_datetime": {"type": "string"},
                "location": {"type": "string"},
                "start_date": {"type": "string"},
                "start_datetime": {"type": "string"},
                "summary": {"type": "string"},
            },
            outputs={
                "summary": {"type": "string"},
                "location": {"type": "string"},
                "description": {"type": "string"},
                "timeZone": {"type": "string"},
                "startTime": {"type": "string"},
                "endTime": {"type": "string"},
            },
            required=["event_id"],
            func=edit_event,
        ),
        Functions(
            name="deleteEvent",
            description="Delete an event after retrieving event ID from listEvents",
            inputs={
                "event_id": {"type": "string"},
            },
            outputs={},
            required=["event_id"],
            func=delete_event,
        ),
    ]
