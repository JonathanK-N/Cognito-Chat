from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from services.gpt_service import get_gpt_response, analyze_image
from services.pdf_service import extract_text_from_pdf_url
from services.whisper_service import transcribe_audio_from_url
from services.tts_service import text_to_speech
from database import save_conversation, get_conversation_history

load_dotenv()

whatsapp_bp = Blueprint('whatsapp', __name__)

# Configuration Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@whatsapp_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook pour recevoir les messages WhatsApp"""
    try:
        # Récupérer les données du message
        from_number = request.form.get('From', '')
        message_body = request.form.get('Body', '')
        media_url = request.form.get('MediaUrl0', '')
        media_content_type = request.form.get('MediaContentType0', '')
        
        response_text = ""
        message_type = "texte"
        
        # Récupérer l'historique de conversation
        conversation_history = get_conversation_history(from_number, 6)
        
        # Traitement selon le type de contenu
        if media_url:
            if 'image' in media_content_type:
                message_type = "image"
                response_text = analyze_image(media_url)
            elif 'pdf' in media_content_type or 'application' in media_content_type:
                message_type = "pdf"
                pdf_text = extract_text_from_pdf_url(media_url)
                if pdf_text and not pdf_text.startswith("Erreur"):
                    response_text = get_gpt_response(f"Analyse ce document PDF:\n\n{pdf_text}", conversation_history=conversation_history)
                else:
                    response_text = pdf_text
            elif 'audio' in media_content_type:
                message_type = "audio"
                transcription = transcribe_audio_from_url(media_url)
                if transcription and not transcription.startswith("Erreur"):
                    response_text = get_gpt_response(f"Réponds à cette transcription audio: {transcription}", conversation_history=conversation_history)
                else:
                    response_text = transcription
            else:
                response_text = "Type de fichier non supporté. Envoyez du texte, PDF, image ou audio."
        elif message_body:
            response_text = get_gpt_response(message_body, conversation_history=conversation_history)
        else:
            response_text = "Bonjour! Envoyez-moi un message texte, PDF, image ou audio."
        
        # Sauvegarder la conversation
        save_conversation(from_number, None, from_number, message_type, message_body or "Fichier média", response_text)
        
        # Créer la réponse Twilio
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        # Optionnel: Envoyer aussi une réponse audio
        if len(response_text) < 500:  # Limiter TTS aux réponses courtes
            try:
                audio_path = text_to_speech(response_text)
                if audio_path:
                    # Envoyer l'audio (nécessite un serveur web pour héberger le fichier)
                    # Pour l'instant, on se contente du texte
                    os.unlink(audio_path)  # Nettoyer
            except:
                pass  # Ignorer les erreurs TTS
        
        return str(twiml_response)
    
    except Exception as e:
        # En cas d'erreur, renvoyer un message d'erreur
        twiml_response = MessagingResponse()
        twiml_response.message(f"Erreur: {str(e)}")
        return str(twiml_response)