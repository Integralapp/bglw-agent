import os
from dotenv import load_dotenv

load_dotenv()

BT_API_KEY = os.getenv("BT_API_KEY", "")
MODEL_ID = os.getenv("MODEL_ID", "")
EMAIL = os.getenv("EMAIL", "jainshreyp@gmail.com")
PASSWORD = os.getenv("PASSWORD", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PC_API_KEY = os.getenv("PC_API_KEY", "")
OAI_API_KEY = os.getenv("OAI_API_KEY", "")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")