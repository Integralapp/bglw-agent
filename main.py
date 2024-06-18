from config import BT_API_KEY, MODEL_ID
from src.llm import generate
from src.email import check_for_emails
import requests

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # check_for_emails()

    generation = generate([{"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"}, {"role": "user", "content": "How are you?"}], stream=False)
    print(generation)