import requests
import os

API_KEY = os.getenv("BT_API_KEY")

BASE_URL = "https://api.baseten.co/v1/models"
MODEL_URL = f"https://model-{os.getenv("MODEL_ID")}.api.baseten.co/production/"

def generate(input: str):
    response = requests.post(
        MODEL_URL + "/predict",
        headers={"Authorization": f"Api-Key {API_KEY}"}
        json=input
    )
    
    return response.json()

def all_models():
    response = requests.get(
        BASE_URL
    )