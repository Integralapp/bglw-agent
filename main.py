from config import BT_API_KEY, MODEL_ID
from src.llm import generate
import requests

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    for chunk in generate([{"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"}, {"role": "user", "content": "Tell me more about the hospitality industry"}], stream=False):
        print(chunk)
