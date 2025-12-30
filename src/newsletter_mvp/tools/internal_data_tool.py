"""
Tool de lecture de données internes
Permet de charger et lire les documents/données internes de l'entreprise.
"""

import json
import os
from crewai.tools import tool


@tool("internal_data_tool")
def load_internal_documents(query: str = "") -> str:
    """
    Charge les documents internes simulés à partir d'un fichier JSON.

    Args:
        query: Optionnel - filtre de recherche (non utilisé dans cette version mock)

    Returns:
        Données internes formatées en texte
    """
    # Chemin vers le fichier de données internes
    data_path = os.path.join(os.getcwd(), "data", "internal_docs.json")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Formater les données pour un affichage lisible
        results = []
        results.append("=== DOCUMENTS INTERNES ===\n")

        for idx, doc in enumerate(data, 1):
            result = f"{idx}. {doc.get('title', 'Sans titre')}\n"
            result += f"   Date: {doc.get('date', 'N/A')}\n"
            result += f"   Contenu: {doc.get('content', 'N/A')}\n"
            if 'category' in doc:
                result += f"   Catégorie: {doc['category']}\n"
            results.append(result)

        return "\n".join(results)

    except FileNotFoundError:
        return f"Erreur: Le fichier {data_path} n'existe pas. Veuillez créer le fichier de données internes."
    except json.JSONDecodeError as e:
        return f"Erreur: Le fichier JSON est mal formaté - {str(e)}"
    except Exception as e:
        return f"Erreur lors de la lecture des données internes: {str(e)}"
