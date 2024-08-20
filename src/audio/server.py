import audioop
import base64
import io
import time
import wave
from flask import Flask, Response
from llm import PhoneCall
from deepgram import DeepgramClient, FileSource, PrerecordedOptions
import asyncio
import websockets
import json
import threading
import textwrap
import numpy as np
from io import BytesIO
from cartesia import Cartesia
from config import GROQ_API_KEY, DEEPGRAM_API_KEY

from prompts import TURA_SYSTEM_PROMPT

app = Flask(__name__)

cartesia = Cartesia(api_key="6cceb273-3856-46a3-a1b7-f9cabae951c4")
model_id = "sonic-english"
voice_id = "156fb8d2-335b-4950-9cb3-a2d33befec77"
experimental_controls = {"speed": "normal","emotion": ["curiosity:high"]}
output_format = {'container': 'raw', 'encoding': 'pcm_mulaw','sample_rate': 8000}

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

log_time = lambda x: print(f"{x}: " + time.strftime('%Y-%m-%d %H:%M:%S'))

# Assume these functions exist
async def custom_tts(websocket, stream_sid, text, *args, **kwargs):
    log_time("Start of TTS")
    for output in cartesia.tts.sse(
        model_id="sonic-english",
        transcript=text,
        voice_id=voice_id,
        _experimental_voice_controls=experimental_controls,
        output_format=output_format,
        stream=True
    ):
        buffer = output["audio"]

        await websocket.send(
            json.dumps(
                {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {
                        "payload": base64.b64encode(buffer).decode("utf-8")
                    }
                }
            )
        )
    log_time("End of TTS")

def custom_stt(audio_data):
    log_time("Start of STT")
    # Check if we have any audio data
    if len(audio_data) == 0:
        print("No audio data to process")
        return ""

    # Print some debug information
    print(f"Audio data length: {len(audio_data)} bytes")

    # Convert audio_data to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    print(f"Audio array min: {audio_array.min()}, max: {audio_array.max()}")
    print(f"Audio array mean: {audio_array.mean()}, std: {audio_array.std()}")
    # Convert the audio data to a WAV file in memory
    wav_file = io.BytesIO()
    with wave.open(wav_file, 'wb') as wav:
        wav.setnchannels(1)  # Mono audio
        wav.setsampwidth(2)  # 16-bit audio
        wav.setframerate(16000)  # Sample rate (adjust if different)
        wav.writeframes(audio_array.tobytes())

    # Reset the BytesIO object to the beginning
    wav_file.seek(0)

    payload: FileSource = {
        "buffer": wav_file,
    }

    options = PrerecordedOptions(
        model="nova-2",
        smart_format=True,
    )

    response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

    transcribed_text = response['results']['channels'][0]['alternatives'][0]['transcript']

    log_time("End of STT")

    return transcribed_text

async def stream_to_bytes(response):
    bytes_io = BytesIO()
    for chunk in response:
        bytes_io.write(chunk)
    return bytes_io.getvalue()

def calculate_rms(audio_chunk):
    mean_squared = max(np.mean(np.square(audio_chunk)), 0)

    return np.sqrt(mean_squared)

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

async def handle_stream(websocket, path):
    buffer = b""
    speech_buffer = b""

    silence_duration = 0
    is_speaking = False
    sample_rate = 16000  # Adjust to match your audio sample rate
    samples_per_chunk = int(sample_rate * 0.1)  # Process in 100ms chunks
    init = False

    # Parameters for dynamic thresholding
    window_duration = 1.0  # 1 second window
    window_size = int(window_duration / 0.1)  # Number of 100ms chunks in the window
    energy_window = []
    scaling_factor = 1.2  # Adjust this value to fine-tune sensitivity

    phone_call = PhoneCall(groq_api_key=GROQ_API_KEY, system_prompt=TURA_SYSTEM_PROMPT)

    try:
        async for message in websocket:
            data = json.loads(message)
            if data["event"] == "media":
                chunk = base64.b64decode(data["media"]["payload"])
                chunk = audioop.ulaw2lin(chunk, 2)
                chunk = audioop.ratecv(chunk, 2, 1, 8000, 16000, None)[0]
                buffer += chunk

                while len(buffer) >= samples_per_chunk * 2:
                    audio_chunk = np.frombuffer(buffer[:samples_per_chunk * 2], dtype=np.int16)
                    buffer = buffer[samples_per_chunk * 2:]

                    chunk_energy = calculate_rms(audio_chunk)
                    energy_window.append(chunk_energy)

                    if len(energy_window) > window_size:
                        energy_window.pop()

                    if len(energy_window) == window_size:
                        dynamic_threshold = np.mean(energy_window) * scaling_factor
                    else:
                        dynamic_threshold = 6  # Use a wdefault value until the window is filled

                    dynamic_threshold = min(dynamic_threshold, 6)

                    if chunk_energy >= dynamic_threshold:
                        print(chunk_energy)
                        if not is_speaking:
                            is_speaking = True
                        silence_duration = 0
                        speech_buffer += audio_chunk.tobytes()
                    else:
                        silence_duration += 0.1
                        if is_speaking:
                            speech_buffer += audio_chunk.tobytes()

                    # Process speech after enough silence
                    if (is_speaking and silence_duration >= 0.5) and len(buffer) != 0:
                        print("Enough Silence Now")
                        is_speaking = False
                        await websocket.send(json.dumps({
                                "event": "media",
                                "streamSid": data["streamSid"],
                                "media": {
                                    "track": "inbound",
                                    "chunk": "start"
                                }
                        }))

                        is_speaking = False
                        transcribed_text = custom_stt(speech_buffer)

                        print("Transcribed text: ", transcribed_text)

                        if not transcribed_text or len(transcribed_text) == 0:
                            # Skip over the rest of this call if there is no text to be transcribed
                            continue

                        log_time("Start of Generation")
                        generation = phone_call(transcribed_text)
                        log_time("End of Generation")

                        print("Groq Generation: ", generation)
                        
                        # This streams output audio directly to the websocket
                        await custom_tts(websocket, data["streamSid"], generation)

                        print("Finished TTS output")

                        speech_buffer = b""
                        silence_duration = 0
                        
                        await websocket.send(json.dumps({
                            "event": "media",
                            "streamSid": data["streamSid"],
                            "media": {
                                "track": "inbound",
                                "chunk": "end"
                            }
                        }))
            elif data["event"] == "start":
                if not init:
                    await custom_tts(
                        websocket,
                        data["streamSid"],
                        "Welcome to Sprezzatura – the most effortless employee you'll ever meet. I'm happy to answer any questions you have about the company!"
                    )
                    init = True
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