from cartesia import Cartesia
import pyaudio
import os

cart = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY", "5cea8ddc-e505-4d16-b651-0e71042f5b15"))

model_id = "sonic-english"
output_format = {
    "container": "raw",
    "encoding": "pcm_f32le",
    "sample_rate": 44100,
}

def text_to_speech(text, voice_id:str = "a0e99841-438c-4a64-b679-ae501e7d6091"):
    try:
        voice = cart.voices.get(id=voice_id)
        print("USING VOICE", voice)

        p = pyaudio.PyAudio()
        rate = 44100

        stream = None

        for output in cart.tts.sse(
            model_id=model_id,
            transcript=text,
            voice_embedding=voice["embedding"],
            stream=True,
            output_format=output_format,
        ):
            buffer = output["audio"]

            if not stream:
                stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=True)

            # Write the audio data to the stream
            stream.write(buffer)
            # yield buffer
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    except Exception as e:
        print(e)
        raise e