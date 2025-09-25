from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from services.gpt_service import get_gpt_response, analyze_image
from services.pdf_service import extract_text_from_pdf
from services.whisper_service import transcribe_audio
from services.tts_service import text_to_speech
from database import save_conversation, get_conversations, get_conversation_history, create_chat_session, get_chat_sessions, get_session_messages, update_session_title, get_user_by_id

def login_required(f):
    """Décorateur pour protéger les routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

web_bp = Blueprint('web', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'ogg'}

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@web_bp.route('/')
@web_bp.route('/chat/<session_id>')
@login_required
def index(session_id=None):
    """Page d'accueil avec interface de chat"""
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    
    if not session_id:
        session_id = create_chat_session(user_id)
        return redirect(f'/chat/{session_id}')
    
    sessions = get_chat_sessions(user_id)
    messages = get_session_messages(session_id)
    return render_template('index.html', sessions=sessions, current_session=session_id, messages=messages, user=user)

@web_bp.route('/chat/<session_id>', methods=['POST'])
@login_required
def chat(session_id):
    """Traite les messages et fichiers depuis l'interface web"""
    try:
        message = request.form.get('message', '').strip()
        file = request.files.get('file')
        
        response_text = ""
        message_type = "texte"
        question = message
        
        # Récupérer l'historique de conversation
        conversation_history = get_conversation_history(session_id, 6)
        
        if file and file.filename and allowed_file(file.filename):
            # Sauvegarder le fichier
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                # Traitement selon le type de fichier
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    message_type = "image"
                    # Analyser l'image locale
                    import base64
                    with open(filepath, 'rb') as img_file:
                        image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    
                    from services.gpt_service import client
                    gpt_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Décris cette image en détail."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                                ]
                            }
                        ],
                        max_tokens=800
                    )
                    response_text = gpt_response.choices[0].message.content.strip()
                    question = f"Image: {filename}" + (f" + Question: {message}" if message else "")
                    
                elif filename.lower().endswith('.pdf'):
                    message_type = "pdf"
                    pdf_text = extract_text_from_pdf(filepath)
                    if pdf_text and not pdf_text.startswith("Erreur"):
                        prompt = f"Analyse ce document PDF:\n\n{pdf_text}"
                        if message:
                            prompt += f"\n\nQuestion spécifique: {message}"
                        response_text = get_gpt_response(prompt, max_tokens=1500, conversation_history=conversation_history)
                        question = f"PDF: {filename}" + (f" + Question: {message}" if message else "")
                    else:
                        response_text = pdf_text
                        
                elif filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                    message_type = "audio"
                    transcription = transcribe_audio(filepath)
                    if transcription and not transcription.startswith("Erreur"):
                        prompt = f"Réponds à cette transcription audio: {transcription}"
                        if message:
                            prompt += f"\n\nContext/Question: {message}"
                        response_text = get_gpt_response(prompt, max_tokens=1500, conversation_history=conversation_history)
                        question = f"Audio: {filename}" + (f" + Question: {message}" if message else "")
                    else:
                        response_text = transcription
                        
            finally:
                # Nettoyer le fichier uploadé
                if os.path.exists(filepath):
                    os.unlink(filepath)
                    
        elif message:
            response_text = get_gpt_response(message, max_tokens=1500, conversation_history=conversation_history)
        else:
            response_text = "Veuillez saisir un message ou uploader un fichier."
        
        # Sauvegarder la conversation
        user_id = session['user_id']
        save_conversation(session_id, user_id, "web-interface", message_type, question, response_text)
        
        # Mettre à jour le titre de la session si c'est le premier message
        if len(conversation_history) == 0 and question:
            title = question[:50] + "..." if len(question) > 50 else question
            update_session_title(session_id, title)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'type': message_type
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@web_bp.route('/new-chat')
@login_required
def new_chat():
    """Crée une nouvelle session de chat"""
    user_id = session['user_id']
    session_id = create_chat_session(user_id)
    return redirect(f'/chat/{session_id}')

@web_bp.route('/voice/<session_id>')
@login_required
def voice_chat(session_id):
    """Page de conversation vocale"""
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    return render_template('voice.html', current_session=session_id, user=user)

@web_bp.route('/history')
@login_required
def history():
    """Affiche l'historique des conversations"""
    conversations = get_conversations(100)
    return render_template('history.html', conversations=conversations)