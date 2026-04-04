from openai import OpenAI
import requests
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception:
    client = None

def transcribe_audio_from_url(audio_url):
    """Transcrit un fichier audio depuis une URL"""
    try:
        # Authentification Twilio pour accéder aux fichiers média
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        response = requests.get(audio_url, auth=(twilio_sid, twilio_token))
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'ogg' in content_type:
            suffix = '.ogg'
        elif 'mp3' in content_type:
            suffix = '.mp3'
        elif 'wav' in content_type:
            suffix = '.wav'
        else:
            suffix = '.mp3'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        transcription = transcribe_audio(temp_path)
        os.unlink(temp_path)
        
        return transcription
    except Exception as e:
        return f"Erreur transcription audio: {str(e)}"

def transcribe_audio(audio_path, language=None):
    """Transcrit un fichier audio local avec Whisper"""
    try:
        with open(audio_path, 'rb') as audio_file:
            params = dict(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                prompt="Cognito Chat, assistant vocal intelligent."
            )
            if language:
                params['language'] = language
            transcript = client.audio.transcriptions.create(**params)
        return transcript if isinstance(transcript, str) else transcript.text
    except Exception as e:
        return f"Erreur Whisper: {str(e)}"