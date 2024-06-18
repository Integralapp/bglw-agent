class Functions(TypedDict):
    function_name: str
    function_inputs: List[Dict[str, str]]
    function_outputs: List[Dict[str, str]]

    def __str__(self):
        inputs = ', '.join(
            [f"{name}: {typ}" for input in self['function_inputs'] for name, typ in input.items()])
        outputs = ', '.join(
            [f"{name}: {typ}" for output in self['function_outputs'] for name, typ in output.items()])
        return f"Function Name: {self['function_name']}\nInputs: {inputs}\nOutputs: {outputs}"

# Hardcoded function retrieval for now
def retrieve_functions():
    return [
        Functions(
            function_name="insertEvent",
            function_inputs={
                "summary": "string",
                "location": "string",
                "description": "string",
                "timeZone": "string",
                "startTime": "string",
                "endTime": "string",
            },
            function_outputs={
                "htmlLink": "string",
            }
        ),
        Functions(
            function_name="listEvents",
            function_inputs={
                "attendee_email": "string",
            },
            function_outputs={
                "summary": "string",
                "location": "string",
                "description": "string",
                "timeZone": "string",
                "startTime": "string",
                "endTime": "string",
            }
        ),
        Functions(
            function_name="editEvent",
            function_inputs={
                "event_id": "string",
                "additional_guests": "optional<list<string>>",
                "end_date": "optional<string>",
                "end_datetime": "optional<string>",
                "location": "optional<string>",
                "start_date": "optional<string>",
                "start_datetime": "optional<string>",
                "summary": "optional<string>"
            },
            function_outputs={
                "summary": "string",
                "location": "string",
                "description": "string",
                "timeZone": "string",
                "startTime": "string",
                "endTime": "string",
            }
        ),
        Functions(
            function_name="deleteEvent",
            function_inputs={
                "eventId": "string",
            },
            function_outputs={}
        )
    ]
