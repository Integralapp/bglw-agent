import json
from config import GROQ_API_KEY
from src.functions import Functions
from typing import List, TypedDict, Dict
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)


class Message(TypedDict):
    role: str
    content: str


def to_tool(func):
    properties = {
        name: {"type": typ["type"]}
        for input in func["inputs"]
        for name, typ in input.items()
    }
    return {
        "type": "function",
        "function": {
            "name": func["name"],
            "description": func["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": func["required"],
            },
        },
    }

to_tool = {
    "insert_event": {
        "type": "function",
        "function": {
            "name": "insert_event",
            "description": "Insert a new event in the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "receiver_email": {"type": "string"},
                        "summary": {"type": "string"},
                        "location": {"type": "string"},
                        "description": {"type": "string"},
                        "timeZone": {"type": "string"},
                        "startTime": {"type": "string"},
                        "endTime": {"type": "string"},
                    },
                    "required": ["receiver_email", "summary", "startTime", "endTime"],
            },
        }
    },
    "delete_event": {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete an event from the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "receiver_email": {"type": "string"},
                    },
                    "required": ["receiver_email"],
                },
        }
    }
}


def _predict_endpoint(
    messages: List[Message],
    functions: List[Functions],
    stream: bool = False,
    *args,
    **kwargs
):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192",
        tools=[to_tool[func["name"]] for func in functions],
        tool_choice="auto",
        max_tokens=4096,
    )

    return chat_completion


def generate(
    messages: List[Message], functions: List[Functions], available_functions: dict[str, any], *args, **kwargs
):
    response = _predict_endpoint(messages, functions, *args, **kwargs)

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    while tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name

            function_to_call = available_functions[function_name]
            function_to_call_args = json.loads(tool_call.function.arguments)

            function_response = function_to_call(**function_to_call_args)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

            response_message = (
                _predict_endpoint(messages, *args, **kwargs).choices[0].messages
            )
            tool_calls = response_message.tool_calls

    return response_message.content
