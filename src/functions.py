from typing import List, Dict, TypedDict, Callable


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
        ),
        Functions(
            name="deleteEvent",
            description="Delete an event after retrieving event ID from listEvents",
            inputs={
                "event_id": {"type": "string"},
            },
            outputs={},
            required=["event_id"],
        ),
    ]
