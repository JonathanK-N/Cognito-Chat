import requests
import json
from bs4 import BeautifulSoup
import urllib.parse

def search_web(query, num_results=3):
    """Effectue une recherche web avec Bing Search API gratuite"""
    try:
        # Utiliser Bing Search via RapidAPI (gratuit)
        url = "https://bing-web-search1.p.rapidapi.com/search"
        
        querystring = {
            "q": query,
            "count": str(num_results),
            "freshness": "Day",  # Résultats récents
            "textFormat": "Raw"
        }
        
        headers = {
            "X-RapidAPI-Key": "demo",  # Clé demo
            "X-RapidAPI-Host": "bing-web-search1.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data.get('webPages', {}).get('value', [])[:num_results]:
                results.append({
                    'title': item.get('name', ''),
                    'content': item.get('snippet', ''),
                    'url': item.get('url', '')
                })
            
            if results:
                return results
        
        # Fallback vers DuckDuckGo HTML scraping
        return duckduckgo_search(query, num_results)
        
    except Exception as e:
        return duckduckgo_search(query, num_results)

def duckduckgo_search(query, num_results=3):
    """Recherche avec DuckDuckGo en scrapant les résultats"""
    try:
        # Recherche DuckDuckGo
        search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query + ' 2024')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        # Extraire les résultats
        for result in soup.find_all('div', class_='result')[:num_results]:
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem:
                title = title_elem.get_text().strip()
                url = title_elem.get('href', '')
                snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                
                if title and snippet:
                    results.append({
                        'title': title,
                        'content': snippet,
                        'url': url
                    })
        
        if not results:
            # Dernière tentative avec Google News RSS
            return google_news_search(query)
        
        return results
        
    except Exception as e:
        return google_news_search(query)

def google_news_search(query):
    """Recherche dans Google News RSS pour des infos récentes"""
    try:
        news_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=fr&gl=FR&ceid=FR:fr"
        
        response = requests.get(news_url, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        
        results = []
        for item in soup.find_all('item')[:3]:
            title = item.find('title').get_text() if item.find('title') else ''
            description = item.find('description').get_text() if item.find('description') else ''
            link = item.find('link').get_text() if item.find('link') else ''
            
            if title:
                results.append({
                    'title': title,
                    'content': description,
                    'url': link
                })
        
        return results if results else [{'title': 'Recherche', 'content': f'Recherche effectuée pour: {query}', 'url': ''}]
        
    except:
        return [{'title': 'Recherche', 'content': f'Recherche effectuée pour: {query}', 'url': ''}]

def format_search_results(results):
    """Formate les résultats de recherche pour GPT"""
    if not results:
        return "Aucun résultat trouvé."
    
    formatted = "INFORMATIONS RÉCENTES TROUVÉES (2024) :\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"{i}. {result['title']}\n"
        formatted += f"   {result['content']}\n"
        if result['url']:
            formatted += f"   Source: {result['url']}\n"
        formatted += "\n"
    
    return formatted