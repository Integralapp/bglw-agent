import base64
from llm import PhoneCall
from stt import speech_to_text
from twilio.rest import Client
from requests import Response
import ngrok
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import json

from tts import text_to_speech

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, CARTESIA_API_KEY, GROQ_API_KEY

print("Auth", TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

TTS_WEBSOCKET_URL = f'wss://api.cartesia.ai/tts/websocket?api_key={CARTESIA_API_KEY}&cartesia_version=2024-06-10'
model_id = 'sonic-english'
voice = {
    'mode': 'id',
    'id': "VOICE_ID" # You can check available voices using the Cartesia API or at https://play.cartesia.ai
}

app = Flask(__name__)

@app.route('/start', methods=['POST'])
def start():
    response = VoiceResponse()
    gather = Gather(input='speech', action='/respond', language='en-US')
    gather.say("Hello, how can I assist you today?")

    response.append(gather)
    response.redirect('/voice')

    return str(response)

@app.route('/respond', methods=['GET', 'POST'])
def respond():
    call = PhoneCall(GROQ_API_KEY)
    speech_result = request.values.get('SpeechResult')

    if speech_result:
        llm_text = call(speech_result)
        response = VoiceResponse()
        response.say(llm_text)
    else:
        response = VoiceResponse()
        response.say("Sorry, I didn't catch that. Can you repeat that for me please?")
    response.redirect('/start')
    return str(response)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
    print("Running app on http://localhost:8000")


