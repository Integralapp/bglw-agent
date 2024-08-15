import os
from dotenv import load_dotenv

load_dotenv()

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVEN_API_KEY = os.getenv("TTS_KEY", "")