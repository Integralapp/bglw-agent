import os
from dotenv import load_dotenv

load_dotenv()

BT_API_KEY = os.getenv("BT_API_KEY", "")
MODEL_ID = os.getenv("MODEL_ID", "")
EMAIL = os.getenv("EMAIL", "jainshreyp@gmail.com")
PASSWORD = os.getenv("PASSWORD", "")