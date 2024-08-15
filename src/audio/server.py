import base64
import io
import time
import wave
from flask import Flask, request, Response
from stt import speech_to_text
from twilio.twiml.voice_response import VoiceResponse, Start
import asyncio
import websockets
import json
from pydub import AudioSegment
import threading
import textwrap
import numpy as np
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from io import BytesIO
from faster_whisper import WhisperModel
import sounddevice as sd
import requests
from config import ELEVEN_API_KEY

app = Flask(__name__)
el = ElevenLabs(
    api_key=ELEVEN_API_KEY
)


# Assume these functions exist
def custom_tts(text, *args, **kwargs):
    response = el.text_to_speech.convert(
        voice_id="pqHfZKP75CvOlQylNhV4",
        model_id='eleven_turbo_v2_5',
        output_format="ulaw_8000",
        text=text,
        voice_settings=VoiceSettings(
            stability=0.1,
            similarity_boost=0.3,
            style=0.2,
        ),
        **kwargs,
    )

    return stream_to_bytes(response)

def custom_stt(audio_data):
    # Check if we have any audio data
    if len(audio_data) == 0:
        print("No audio data to process")
        return ""

    # Print some debug information
    print(f"Audio data length: {len(audio_data)} bytes")

    # Convert audio_data to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # Play the audio
    sd.play(audio_array, samplerate=8000)
    sd.wait()  # Wait for the audio to finish playing

    # Convert the audio data to a WAV file in memory
    wav_file = io.BytesIO()
    with wave.open(wav_file, 'wb') as wav:
        wav.setnchannels(1)  # Mono audio
        wav.setsampwidth(2)  # 16-bit audio
        wav.setframerate(8000)  # Sample rate (adjust if different)
        wav.writeframes(audio_data)

    # Reset the BytesIO object to the beginning
    wav_file.seek(0)

    # Initialize the Whisper model (you may want to do this once and reuse)
    model = WhisperModel("base", device="cpu", compute_type="int8")

    # Transcribe the audio
    segments, info = model.transcribe(wav_file, beam_size=5)

    # Extract the transcribed text
    transcribed_text = " ".join(segment.text for segment in segments)

    return transcribed_text

async def stream_to_bytes(response):
    bytes_io = BytesIO()
    for chunk in response:
        bytes_io.write(chunk)
    return bytes_io.getvalue()

@app.route('/twiml', methods=['POST'])
def return_twiml():
    try:
        twiml = textwrap.dedent("""
        <Response>
            <Connect>
                <Stream url="wss://sound.ngrok.app/" />
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
    speech_buffer = b""
    silence_threshold = 8500  # Adjust this value based on your audio characteristics
    silence_duration = 0
    is_speaking = False
    sample_rate = 8000  # Adjust to match your audio sample rate
    samples_per_chunk = int(sample_rate * 0.1)  # Process in 100ms chunks
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["event"] == "media":
                chunk = base64.b64decode(data["media"]["payload"])
                buffer += chunk

                while len(buffer) >= samples_per_chunk * 2:
                    audio_chunk = np.frombuffer(buffer[:samples_per_chunk * 2], dtype=np.int16)
                    buffer = buffer[samples_per_chunk * 2:]

                    chunk_amplitude = np.abs(audio_chunk).mean()
                    
                    if chunk_amplitude >= silence_threshold:
                        print(chunk_amplitude)
                        if not is_speaking:
                            is_speaking = True
                        silence_duration = 0
                        speech_buffer += audio_chunk.tobytes()
                    else:
                        silence_duration += 0.1
                        if is_speaking:
                            speech_buffer += audio_chunk.tobytes()

                    # Process speech after enough silence
                    if is_speaking and silence_duration >= 0.5:
                        print("Enough Silence Now")
                        is_speaking = False
                        if len(speech_buffer) > 0:
                            # full_audio = np.frombuffer(speech_buffer, dtype=np.int16)
                            transcribed_text = custom_stt(speech_buffer)
                            speech_buffer = b""
                            silence_duration = 0

                            response_text = f"I heard you say: {transcribed_text}"
                            print(response_text)

                        #     await websocket.send(json.dumps({
                        #         "event": "media",
                        #         "streamSid": data["streamSid"],
                        #         "media": {
                        #             "track": "inbound",
                        #             "chunk": "start"
                        #         }
                        #     }))

                        #     audio_data = custom_tts(transcribed_text)

                        #     await websocket.send(json.dumps({
                        #         "event": "media",
                        #         "streamSid": data["streamSid"],
                        #         "media": {
                        #             "payload": base64.b64encode(audio_data).decode("utf-8")
                        #         }
                        #     }))

                        # await websocket.send(json.dumps({
                        #     "event": "media",
                        #     "streamSid": data["streamSid"],
                        #     "media": {
                        #         "track": "inbound",
                        #         "chunk": "end"
                        #     }
                        # }))
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