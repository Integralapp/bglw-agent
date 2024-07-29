from groq import Groq
from typing import List, TypedDict

class Message(TypedDict):
    role: str
    content: str

class PhoneCall:
  def __init__(self, groq_api_key, system_prompt=""):
    self.system = system_prompt
    self.messages = []
    self.client = Groq(api_key=groq_api_key)

    if self.system:
      self.messages.append({"role": "system", "content": system_prompt})

  def __call__(self, message):
    self.messages.append({"role": "user", "content": message})
    result = self.execute()
    self.messages.append({"role": "assistant", "content": result})
    return result

  def execute(self, stream: bool = False):
    completion = self.client.chat.completions.create(model="llama3-70b-8192", messages=self.messages, max_tokens=8192, stream=stream)

    return completion.choices[0].message.content
