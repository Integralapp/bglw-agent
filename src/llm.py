from openai import OpenAI
import os

API_KEY = os.getenv("BT_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

client = OpenAI(
    api_key=API_KEY,
    base_url=f"https://bridge.baseten.co/{MODEL_ID}/v1"
)