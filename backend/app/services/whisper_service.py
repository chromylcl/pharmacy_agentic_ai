import whisper
import tempfile
import os

# Load once at startup
model = whisper.load_model("base")


def transcribe_audio(upload_file):
    """
    Convert uploaded audio -> text
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(upload_file.file.read())
        temp_path = tmp.name

    result = model.transcribe(temp_path)

    os.remove(temp_path)

    return result["text"]