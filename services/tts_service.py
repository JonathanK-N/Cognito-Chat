from gtts import gTTS
import tempfile
import os

def text_to_speech(text, lang='fr'):
    """Convertit du texte en audio avec gTTS"""
    try:
        # Créer le fichier audio temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        # Générer l'audio
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_path)
        
        return temp_path
    except Exception as e:
        print(f"Erreur TTS: {str(e)}")
        return None

def text_to_speech_openai(text):
    """Convertit du texte en audio avec OpenAI TTS (alternative)"""
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        response.stream_to_file(temp_path)
        return temp_path
    except Exception as e:
        print(f"Erreur OpenAI TTS: {str(e)}")
        return None