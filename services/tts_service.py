import os
import re
from dotenv import load_dotenv

load_dotenv()

def tts_to_bytes(text, voice="nova"):
    """
    Convertit du texte en audio MP3 via OpenAI TTS.
    Voix disponibles : alloy, echo, fable, onyx, nova, shimmer
    Retourne les bytes MP3 ou None en cas d'erreur.
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Nettoyer tout markdown résiduel avant synthèse
        clean = re.sub(r'```[\s\S]*?```', '', text)   # blocs de code
        clean = re.sub(r'`[^`]+`', '', clean)          # inline code
        clean = re.sub(r'#{1,6}\s+', '', clean)        # titres
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean) # gras
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)     # italique
        clean = re.sub(r'__(.+?)__', r'\1', clean)
        clean = re.sub(r'^\s*[-*+]\s+', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean)
        clean = re.sub(r'[_~|]', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()

        if not clean:
            return None

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=clean[:4096],
            response_format="mp3"
        )
        return response.content

    except Exception as e:
        print(f"[TTS ERROR] {e}")
        return None


# Compatibilité avec l'ancien code (WhatsApp / upload audio)
def text_to_speech(text, lang='fr'):
    """Ancien wrapper gTTS — redirige vers OpenAI TTS"""
    import tempfile
    audio_bytes = tts_to_bytes(text)
    if not audio_bytes:
        # Fallback gTTS
        try:
            from gtts import gTTS
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                gTTS(text=text, lang=lang, slow=False).save(f.name)
                return f.name
        except Exception:
            return None
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
        f.write(audio_bytes)
        return f.name
