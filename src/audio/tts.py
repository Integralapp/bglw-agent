from cartesia import Cartesia
import requests
import pyaudio
import wave
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
    
DEEPTUNE_URL = "https://prod-api-studio.deeptune.ai/v1/speech/demo"
dt_config = {
    "prompt_audio_uri": {
        "uri": "https://deeptune-voices.s3.amazonaws.com/polle/inference/134f5087-6b5b-4e27-87b5-a1d5d01056a0.wav"
    },
    "target_language": "ENGLISH",
}
chunk = 1024

def deeptune_tts(text, voice_id: str = ""):
    dt_config["target_text"] = text

    response = requests.post(
        DEEPTUNE_URL,
        data=dt_config
    )

    out = response.json()

    url = out.get("results", [])[0].get("url", None)

    if not url:
        return
    
    f = wave.open(r"/usr/share/sounds/alsa/Rear_Center.wav","rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  
    
    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    #stop stream  
    stream.stop_stream()  
    stream.close()

