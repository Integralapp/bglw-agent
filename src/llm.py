from typing import List, TypedDict
from requests import post
from config import BT_API_KEY, MODEL_ID

BT_URL = f"https://model-{MODEL_ID}.api.baseten.co/production/predict"

class Message(TypedDict):
    role: str
    content: str

def _predict_endpoint(messages: List[Message], stream: bool = False, *args, **kwargs):
    response = post(
        BT_URL,
        headers={
            "Authorization": f"Api-Key {BT_API_KEY}"
        },
        json={"messages": messages},
        stream=stream,
        **kwargs
    )

    if stream:
        for content in response.iter_content():
            if content:
                yield content.decode("utf-8")
    else:
        return response.content

def generate(messages: List[Message], *args, **kwargs):
   return _predict_endpoint(messages, *args, **kwargs)