from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def _predict_endpoint(
    messages: List[Message],
    # functions: List[Functions],
    stream: bool = False,
    *args,
    **kwargs
):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192",
        max_tokens=4096,
    )

    return chat_completion

@app.route("/voice", methods=['POST'])
def voice():
    # Get the caller's input from Twilio request
    caller_input = request.values.get('SpeechResult', '')

    # Generate AI response
    ai_response = generate_ai_response(caller_input)

    # Create TwiML response
    response = VoiceResponse()
    response.say(ai_response)

    return Response(str(response), mimetype='text/xml')