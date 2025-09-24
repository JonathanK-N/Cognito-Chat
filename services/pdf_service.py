import PyPDF2
import requests
import tempfile
import os

def extract_text_from_pdf_url(pdf_url):
    """Extrait le texte d'un PDF depuis une URL"""
    try:
        # Télécharger le PDF
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        # Extraire le texte
        text = extract_text_from_pdf(temp_path)
        
        # Nettoyer le fichier temporaire
        os.unlink(temp_path)
        
        return text
    except Exception as e:
        return f"Erreur extraction PDF: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF local"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Limiter à 2000 tokens (approximativement 8000 caractères)
        if len(text) > 8000:
            text = text[:8000] + "... [texte tronqué]"
        
        return text.strip()
    except Exception as e:
        return f"Erreur lecture PDF: {str(e)}"