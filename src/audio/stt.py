import os
from faster_whisper import WhisperModel
from io import BytesIO

model_name = "large-v3"
fn = os.path.dirname(__file__) + "/sample_audio.m4a"
model = WhisperModel(model_name, device="cpu", compute_type="int8")

def speech_to_text(audio_bytes):
    segments, info = model.transcribe(BytesIO(audio_bytes), beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    # This is a generator object, so all of the actual model calls will only happen as you iterate
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    return segments
