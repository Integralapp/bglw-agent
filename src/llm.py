from config import BT_API_KEY, MODEL_ID

import re

from typing import List, TypedDict
from requests import post

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
        json={"messages": messages, "max_tokens": 4000, "stream": stream},
        **kwargs
    )

    return response.json()["output"]

def generate(messages: List[Message], *args, **kwargs):
   return _predict_endpoint(messages, *args, **kwargs)