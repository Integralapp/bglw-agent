from config import GROQ_API_KEY

import re

from typing import List, TypedDict
from groq import Groq

client = Groq(
    api_key=GROQ_API_KEY
)

class Message(TypedDict):
    role: str
    content: str

def _predict_endpoint(messages: List[Message], stream: bool = False, *args, **kwargs):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192"
    )

    return chat_completion.choices[0].message.content

def generate(messages: List[Message], *args, **kwargs):
   return _predict_endpoint(messages, *args, **kwargs)