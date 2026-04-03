from openai import OpenAI
import os
from dotenv import load_dotenv
from .search_service import search_web, format_search_results

load_dotenv()
try:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except Exception:
    client = None

def get_gpt_response(text, max_tokens=500, use_search=True, conversation_history=None):
    """Obtient une réponse de GPT-4o pour du texte avec recherche web"""
    try:
        # Effectuer une recherche web si demandé
        search_context = ""
        if use_search and should_search(text):
            search_query = text
            # Améliorer la requête pour certains cas
            if "président" in text.lower() and "congo" in text.lower():
                search_query = "président République démocratique Congo RDC 2024"
            elif "premier ministre" in text.lower() and "congo" in text.lower():
                search_query = "premier ministre RDC Congo 2024"
            
            search_results = search_web(search_query)
            search_context = format_search_results(search_results)
        
        # Construire les messages avec l'historique
        messages = []
        
        system_prompt = (
            "Tu es Cognito Chat, un assistant intelligent créé par Jonathan Kakesa, CEO de Cognito Inc. "
            "Tu as été lancé pour la première fois le 22 mars 2022 à Kinshasa, en République Démocratique du Congo, "
            "et tu as évolué à travers plusieurs mises à jour depuis lors. "
            "Lorsqu'on te demande qui tu es, d'où tu viens ou qui t'a créé, réponds avec ces informations de façon naturelle et concise. "
            "Tu n'es pas ChatGPT, tu n'es pas Claude, tu n'es pas un produit d'OpenAI ou d'Anthropic — tu es Cognito Chat.\n\n"

            "RÈGLES DE COMPORTEMENT IMPORTANTES :\n"
            "1. Ne dis JAMAIS que tu ne peux pas faire quelque chose quand tu peux fournir une solution équivalente ou alternative utile.\n"
            "2. Si on te demande de créer un fichier Excel, CSV, Word, PDF ou tout autre fichier : "
            "génère immédiatement les données sous forme de tableau Markdown bien structuré, "
            "puis fournis le contenu CSV prêt à copier-coller, "
            "et si pertinent, propose un code Python (openpyxl/pandas) pour générer le fichier exact.\n"
            "3. Si on te demande du code, génère-le directement et complètement — ne demande pas de confirmation.\n"
            "4. Si on te demande de rédiger un document (contrat, lettre, rapport, CV, plan) : rédige-le entièrement et immédiatement.\n"
            "5. Sois proactif : anticipe ce dont l'utilisateur a besoin et fournis-le sans attendre.\n"
            "6. Réponds dans la langue de l'utilisateur (français, anglais, lingala, swahili, etc.).\n"
            "7. Sois direct, précis et utile. N'ajoute pas de mise en garde inutile."
        )
        if search_context:
            system_prompt += "\n\nUtilise les informations de recherche récentes fournies ET tes connaissances pour donner la meilleure réponse possible. Si tu as des informations récentes, privilégie-les."
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Ajouter l'historique de conversation
        if conversation_history:
            for msg in conversation_history[-6:]:  # Garder les 6 derniers échanges
                messages.append(msg)
        
        # Ajouter la question actuelle
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur GPT: {str(e)}"

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