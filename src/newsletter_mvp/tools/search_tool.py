"""
Tool de recherche web via Serper.dev
Permet de rechercher des articles et contenus récents sur un sujet donné.
"""

import os
from crewai_tools import tool
import requests


@tool("search_tool")
def search_articles(topic: str) -> str:
    """
    Recherche des articles récents sur un sujet donné via l'API Serper.dev.

    Args:
        topic: Le sujet à rechercher

    Returns:
        Résultats de recherche formatés en texte
    """
    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        return "Erreur: SERPER_API_KEY non définie dans les variables d'environnement"

    try:
        url = "https://google.serper.dev/search"
        payload = {
            "q": topic,
            "num": 10
        }
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Formater les résultats
        results = []
        if "organic" in data:
            for idx, item in enumerate(data["organic"][:10], 1):
                result = f"{idx}. {item.get('title', 'Sans titre')}\n"
                result += f"   Source: {item.get('link', 'N/A')}\n"
                result += f"   Snippet: {item.get('snippet', 'N/A')}\n"
                results.append(result)

        if results:
            return "\n".join(results)
        else:
            return "Aucun résultat trouvé pour cette recherche."

    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la recherche web: {str(e)}"
    except Exception as e:
        return f"Erreur inattendue: {str(e)}"
