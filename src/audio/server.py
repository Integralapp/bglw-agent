import audioop
import base64
import io
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
voice_embedding = [0.029945856,0.017176697,-0.049459293,-0.16836515,-0.11095251,-0.046026077,0.14643976,0.055433456,-0.1024197,-0.001620749,-0.057019018,0.006192061,0.013129239,-0.150381,0.14809933,0.051971216,-0.050541658,-0.05123066,-0.08106663,0.10420144,-0.005546602,0.053035494,-0.02481496,-0.05279231,0.041590605,0.13388915,0.081940375,-0.042714383,0.008637148,0.08455725,-0.042541035,-0.02705292,-0.09113716,-0.093402736,-0.0070344373,0.052490674,-0.047301695,-0.039776657,0.06297582,-0.012005808,-0.04687977,0.04304074,-0.030598763,-0.026485696,-0.07833848,-0.042867865,0.013610328,-0.10315587,0.018464237,0.007744045,-0.074694246,0.0029017352,0.040088326,-0.038031735,-0.19359167,-0.035225388,0.04939342,-0.088448636,-0.09964313,-0.018046405,-0.055259846,-0.103243366,-0.072670415,-0.124953,-0.0030216074,0.050610628,0.109969385,0.027975723,-0.002217993,-0.07239473,-0.0023676085,-0.00013823614,0.02692902,0.045959838,-0.09276329,0.110857025,-0.021394629,0.011870483,0.008720903,-0.041679215,0.124747895,-0.056236252,0.047026537,0.009577025,0.011429973,-0.041923188,-0.0349152,-0.03235487,0.030358737,0.07581399,0.11147319,-0.08668697,-0.049714424,-0.028163848,0.18080874,0.029635996,-0.037455752,-0.04308786,-0.08783033,-0.013554636,-0.022448808,-0.028385311,0.118919425,0.023110593,-0.04605775,-0.043148905,-0.013919928,-0.007947111,0.035668027,0.016373198,-0.035438515,0.03363095,-0.12626375,-0.044032928,0.06886493,-0.005543194,0.050734784,0.014788171,0.008977486,-0.085592136,-0.13210186,-0.034694966,0.076021045,0.10686303,0.2167193,0.077260874,0.006526452,0.0435806,-0.04240478,0.13209686,-0.046833646,0.0031460638,0.17598641,-0.058173247,0.16259913,0.041984487,-0.052617334,0.055540215,-0.046876438,0.021498023,-0.009985289,0.028356465,-0.08830881,-0.014453896,0.0064929123,0.08649789,-0.042999182,0.08144387,-0.0023113969,-0.03666702,0.042809207,0.075711794,0.02095867,0.019503865,-0.064866,0.060052752,-0.1553588,-0.106299534,0.13148177,-0.11918356,-0.0049787583,0.046982054,0.043224636,-0.026665024,0.04482816,-0.07470057,0.01807425,-0.027169084,-0.051037513,-0.07046653,-0.09478667,0.12462844,-0.018405393,-0.0571506,-0.021548841,-0.011105743,-0.1443996,-0.04457995,-0.0035385247,-0.037368357,0.022151444,-0.022209287,-0.036807127,0.0008113249,-0.09231095,0.02567849,0.0013234912,0.018370816,0.10352099,-0.18260677,0.12838842,-0.056870475]
output_format = {'container': 'raw', 'encoding': 'pcm_mulaw','sample_rate': 8000}

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Assume these functions exist
async def custom_tts(websocket, stream_sid, text, *args, **kwargs):
    for output in cartesia.tts.sse(
        model_id="sonic-english",
        transcript=text,
        voice_embedding=voice_embedding,
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

def custom_stt(audio_data):
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

    return transcribed_text

async def stream_to_bytes(response):
    bytes_io = BytesIO()
    for chunk in response:
        bytes_io.write(chunk)
    return bytes_io.getvalue()

def calculate_rms(audio_chunk):
    return np.sqrt(np.mean(np.square(audio_chunk)))

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

                        generation = phone_call(transcribed_text)

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