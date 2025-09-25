from openai import OpenAI
import os
from dotenv import load_dotenv
from .search_service import search_web, format_search_results

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
        
        system_prompt = "Tu es un assistant intelligent qui donne des réponses précises et utiles. Réponds toujours de manière directe et factuelle."
        if search_context:
            system_prompt += " Utilise les informations de recherche récentes fournies ET tes connaissances pour donner la meilleure réponse possible. Si tu as des informations récentes, privilégie-les."
        
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

def analyze_image(image_url):
    """Analyse une image avec GPT-4o Vision"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Décris cette image et réponds à toute question qu'elle pourrait soulever."},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur analyse image: {str(e)}"

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