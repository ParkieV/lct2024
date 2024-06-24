import base64
import os
import tempfile

from api.src.configurations.models import whisper_model

def save_base64_to_temp_file(base64_string):
    audio_data = base64.b64decode(base64_string)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.write(audio_data)
    temp_file.close()
    
    return temp_file.name

def transcribe_audio(audio_string: str):
    try:
        audio = save_base64_to_temp_file(audio_string)
        result = whisper_model.transcribe(audio, language="ru", initial_prompt="Я бы хотел заказать товар под названием")
        os.remove(audio)
        return {'user_prompt': result['text']}
    except FileNotFoundError as e:
        if 'ffmpeg' in str(e):
            return {'error': 'FFmpeg is not installed or not found in PATH.'}
        else:
            return {'error': str(e)}