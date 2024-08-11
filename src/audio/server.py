from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Start
import asyncio
import websockets
import json
import base64
import threading
import textwrap

app = Flask(__name__)

# Assume these functions exist
def custom_tts(text):
    return b"audio_data"

def custom_stt(audio_data):
    return "transcribed text"

@app.route('/twiml', methods=['POST'])
def return_twiml():
    try:
        twiml = textwrap.dedent("""
        <Response>
            <Connect>
                <Stream url="ws://ngrok." />
            </Connect>
            <Say>This TwiML instruction is unreachable unless the Stream is ended by your WebSocket server.</Say>
        </Response>
        """)
        return Response(twiml, content_type='application/xml'), 200
    except Exception as e:
        return Response(str(e), content_type='text/plain'), 500

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    start = Start()
    stream_url = f"wss://{request.host}:8001/stream"
    print(f"Setting stream URL to: {stream_url}")
    start.stream(url=stream_url)
    response.append(start)
    return str(response)

async def handle_stream(websocket, path):
    buffer = b""
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["event"] == "media":
                chunk = base64.b64decode(data["media"]["payload"])
                buffer += chunk

                if len(buffer) >= 4000:  # Adjust this value as needed
                    transcribed_text = custom_stt(buffer)
                    buffer = b""

                    response_text = f"I heard you say: {transcribed_text}"
                    audio_data = custom_tts(response_text)

                    await websocket.send(json.dumps({
                        "event": "media",
                        "streamSid": data["streamSid"],
                        "media": {
                            "payload": base64.b64encode(audio_data).decode("utf-8")
                        }
                    }))
            elif data["event"] == "start":
                print("Stream started")
            elif data["event"] == "stop":
                print("Stream stopped")
                break
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")

def run_flask():
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)

def run_websocket_server():
    async def serve():
        async with websockets.serve(handle_stream, "0.0.0.0", 8001):
            await asyncio.Future()  # run forever

    asyncio.run(serve())

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    websocket_thread = threading.Thread(target=run_websocket_server)

    flask_thread.start()
    websocket_thread.start()

    flask_thread.join()
    websocket_thread.join()