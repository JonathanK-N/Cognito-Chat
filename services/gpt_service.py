from openai import OpenAI
import os
from dotenv import load_dotenv
from .search_service import search_web, format_search_results

load_dotenv()
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception:
    client = None

def get_gpt_response(text, max_tokens=2500, use_search=True, conversation_history=None):
    """
    Obtient une réponse de GPT-4o avec recherche web.
    Retourne (response_text, sources) où sources est une liste de dicts {title, url}.
    """
    try:
        search_context = ""
        sources = []

        if use_search and should_search(text):
            search_query = text
            if "président" in text.lower() and "congo" in text.lower():
                search_query = "président République démocratique Congo RDC 2024"
            elif "premier ministre" in text.lower() and "congo" in text.lower():
                search_query = "premier ministre RDC Congo 2024"

            search_results = search_web(search_query)
            search_context = format_search_results(search_results)

            # Garder uniquement les sources avec URL valide
            sources = [
                {'title': r['title'], 'url': r['url']}
                for r in search_results
                if r.get('url') and r['url'].startswith('http')
            ]

        messages = []

        system_prompt = (
            "Tu es Cognito Chat, un assistant intelligent créé par Jonathan Kakesa, CEO de Cognito Inc. "
            "Tu as été lancé pour la première fois le 22 mars 2022 à Kinshasa, en République Démocratique du Congo, "
            "et tu as évolué à travers plusieurs mises à jour depuis lors. "
            "Lorsqu'on te demande qui tu es, d'où tu viens ou qui t'a créé, réponds avec ces informations de façon naturelle et concise. "
            "Tu n'es pas ChatGPT, tu n'es pas Claude, tu n'es pas un produit d'OpenAI ou d'Anthropic — tu es Cognito Chat.\n\n"
            "RÈGLES DE COMPORTEMENT IMPORTANTES :\n"
            "1. Ne dis JAMAIS que tu ne peux pas faire quelque chose quand tu peux fournir une solution équivalente ou alternative utile.\n"
            "2. Si on te demande de générer une image, le système la génère automatiquement — réponds positivement en une phrase courte, sans URL ni balise.\n"
            "3. Si on te demande un fichier (Excel, CSV, Word, PDF) : génère le contenu en tableau Markdown structuré.\n"
            "4. Si on te demande du code, génère-le directement et complètement.\n"
            "5. Si on te demande un document (contrat, lettre, rapport, CV) : rédige-le entièrement.\n"
            "6. Sois proactif : anticipe ce dont l'utilisateur a besoin.\n"
            "7. Réponds dans la langue de l'utilisateur (français, anglais, lingala, swahili, etc.).\n"
            "8. Sois direct, précis et utile. N'ajoute pas de mise en garde inutile.\n"
            "9. Ne mentionne JAMAIS les URLs ou sources dans ta réponse — elles sont affichées automatiquement sous ta réponse."
        )
        if search_context:
            system_prompt += "\n\nUtilise les informations de recherche récentes fournies ET tes connaissances. Privilégie les infos récentes."

        messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append(msg)

        user_content = text
        if search_context:
            user_content = f"Informations récentes trouvées:\n{search_context}\n\nQuestion: {text}"

        messages.append({"role": "user", "content": user_content})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content.strip(), sources

    except Exception as e:
        return f"Erreur GPT: {str(e)}", []

def generate_image(prompt, size="1024x1024"):
    """Génère une image avec DALL-E 3 et retourne (url, error_message)"""
    # Prompt trop court ou invalide (CSS, code, lien…) → refus propre
    if len(prompt.strip()) < 5 or '{' in prompt or 'http' in prompt.lower():
        return None, "Le prompt fourni n'est pas valide pour générer une image."
    if size not in {"1024x1024", "1792x1024", "1024x1792"}:
        size = "1024x1024"
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        return response.data[0].url, None
    except Exception as e:
        err = str(e)
        print(f"[DALL-E ERROR] {err}")
        if 'content_policy' in err or 'safety' in err.lower():
            return None, "Cette demande ne respecte pas les règles de contenu de DALL-E. Reformule ta description."
        if 'billing' in err.lower() or 'quota' in err.lower() or 'rate' in err.lower():
            return None, "Limite de génération d'images atteinte. Réessaie dans quelques instants."
        return None, "La génération d'image a échoué. Réessaie avec une description plus précise."

def should_generate_image(text):
    """Détecte si l'utilisateur demande une génération d'image"""
    # Exclure les messages qui semblent être des plaintes / erreurs
    complaint_words = ['erreur', 'error', 'marche pas', 'fonctionne pas', 'problème',
                       'broken', 'bug', 'crash', 'invalide', 'échoué']
    text_lower = text.lower()
    if any(w in text_lower for w in complaint_words):
        return False

    keywords = [
        'génère', 'genere', 'générer', 'generer', 'crée', 'cree', 'créer', 'creer',
        'dessine', 'dessiner', 'illustre', 'illustrer', 'imagine', 'imaginer',
        'fais moi', 'fais-moi', 'montre moi', 'montre-moi',
        'generate', 'create', 'draw', 'make', 'show me',
        'une image', 'un dessin', 'une illustration', 'une photo', 'un tableau',
        'an image', 'a picture', 'a photo', 'a drawing'
    ]
    image_words = [
        'image', 'photo', 'dessin', 'illustration', 'picture', 'drawing',
        'tableau', 'visuel', 'logo', 'icone', 'icône', 'bannière', 'banniere',
        'affiche', 'poster', 'portrait', 'paysage', 'background', 'wallpaper',
        'avatar', 'thumbnail', 'cover', 'art', 'artwork', 'sketch', 'render'
    ]
    has_action = any(k in text_lower for k in keywords)
    has_image_word = any(w in text_lower for w in image_words)
    logo_pattern = any(p in text_lower for p in ['ton logo', 'mon logo', 'un logo', 'le logo', 'son logo', 'notre logo'])
    return (has_action and has_image_word) or logo_pattern

def is_image_followup(text, conversation_history):
    """Détecte si le message est une COURTE affirmation après une proposition d'image du bot"""
    # Exclure les messages qui semblent des plaintes
    complaint_words = ['erreur', 'error', 'marche pas', 'fonctionne pas', 'problème',
                       'lien', 'link', 'broken', 'bug', 'échoué', 'invalide']
    text_lower = text.lower().strip()
    if any(w in text_lower for w in complaint_words):
        return False

    affirmations = [
        'vas-y', 'vasy', 'ok', 'oui', 'yes', 'go', 'génère', 'genere',
        'fais-le', 'fais le', 'lance', 'allez', 'pourquoi pas', 'bien sûr',
        "d'accord", 'parfait', 'super', 'yes please', 'do it', 'allons-y'
    ]
    is_short_affirmation = len(text.split()) <= 4 and any(a in text_lower for a in affirmations)
    if not is_short_affirmation:
        return False

    # Vérifier que le dernier message du bot proposait bien une image
    image_intent_phrases = [
        'image', 'générer', 'generer', 'logo', 'illustration', 'visuel',
        'représentation', 'representation', 'dall-e', 'dessiner', 'créer'
    ]
    if conversation_history:
        for msg in reversed(conversation_history):
            if msg.get('role') == 'assistant':
                last_bot = msg.get('content', '').lower()
                return any(p in last_bot for p in image_intent_phrases)
    return False

def extract_image_prompt_from_history(conversation_history):
    """Retrouve la vraie demande d'image de l'utilisateur dans l'historique"""
    image_request_keywords = [
        'logo', 'image', 'dessin', 'illustration', 'photo', 'genere', 'génère',
        'crée', 'cree', 'dessine', 'picture', 'draw', 'avatar', 'bannière'
    ]
    if conversation_history:
        for msg in reversed(conversation_history):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if any(k in content.lower() for k in image_request_keywords):
                    return content
    return None

def analyze_image_base64(image_base64, prompt="Décris cette image en détail."):
    """Analyse une image encodée en base64 avec GPT-4o Vision"""
    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            max_tokens=800
        )
        return gpt_response.choices[0].message.content.strip()
    except Exception as e:
        return f"Impossible d'analyser l'image: {str(e)[:100]}"

def analyze_image(image_url):
    """Analyse une image avec GPT-4o Vision"""
    try:
        import requests
        import base64
        
        # Télécharger l'image avec authentification Twilio
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not twilio_sid or not twilio_token:
            return "Configuration Twilio manquante pour analyser l'image."
        
        response = requests.get(image_url, auth=(twilio_sid, twilio_token), timeout=30)
        response.raise_for_status()
        
        # Vérifier la taille (limite: 5MB pour éviter les timeouts)
        if len(response.content) > 5 * 1024 * 1024:
            return "Image trop volumineuse. Veuillez envoyer une image plus petite (max 5MB)."
        
        # Encoder en base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # Analyser avec GPT-4o Vision
        gpt_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Décris cette image en quelques phrases."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            max_tokens=150
        )
        return gpt_response.choices[0].message.content.strip()
    except requests.exceptions.Timeout:
        return "Timeout lors de l'analyse de l'image. Réessayez."
    except Exception as e:
        return f"Impossible d'analyser l'image: {str(e)[:100]}"

def get_voice_response(text, conversation_history=None):
    """
    Réponse GPT-4o optimisée pour la synthèse vocale.
    Ton conversationnel naturel, pas de markdown, phrases courtes.
    """
    try:
        messages = []

        voice_system = (
            "Tu es Cognito Chat, un assistant intelligent créé par Jonathan Kakesa, CEO de Cognito Inc. "
            "Tu réponds à l'oral, comme dans une vraie conversation humaine.\n\n"
            "RÈGLES ABSOLUES POUR LE VOCAL :\n"
            "1. Maximum 3 à 5 phrases par réponse — sois concis et naturel.\n"
            "2. N'utilise JAMAIS de markdown : pas de *, **, #, -, listes, blocs de code.\n"
            "3. Parle comme un humain : contractions, transitions naturelles (« En fait », « Donc », « Du coup »…).\n"
            "4. Si la question est complexe, donne l'essentiel d'abord et propose d'aller plus loin.\n"
            "5. Utilise la langue de l'utilisateur (français, anglais, lingala…).\n"
            "6. Ne dis jamais que tu es une IA — parle simplement et avec confiance."
        )

        messages.append({"role": "system", "content": voice_system})

        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append(msg)

        messages.append({"role": "user", "content": text})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=350,
            temperature=0.65
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Désolé, je n'ai pas pu traiter ta demande. Réessaie."


def should_search(text):
    """Détermine si une recherche web est nécessaire"""
    search_keywords = [
        'qui est', 'c’est qui', 'actuel', 'premier ministre', 'président',
        'actualité', 'news', 'récent', 'aujourd’hui', 'maintenant', 'prix', 'coût',
        'où', 'quand', 'qu’est-ce que', 'comment', 'pourquoi', 'gouvernement',
        'information', 'recherche', 'trouve', 'cherche', 'meteo', 'météo',
        'bourse', 'action', 'crypto', 'bitcoin', 'cours', 'taux', 'ministre',
        'congo', 'rdc', 'kinshasa', 'politique', 'dirigeant'
    ]
    
    text_lower = text.lower()
    # Recherche si la question contient des mots-clés ou semble être une question factuelle
    return (any(keyword in text_lower for keyword in search_keywords) or 
            text_lower.endswith('?') and len(text.split()) > 2)