#!/usr/bin/env python
"""
Point d'entrée principal pour la génération automatique de newsletters
"""

import os
from dotenv import load_dotenv
from newsletter_mvp.crew import NewsletterMvpCrew


def main():
    """
    Lance le processus de génération de newsletter
    """
    # Charger les variables d'environnement depuis .env
    load_dotenv()

    # Vérifier que les clés API essentielles sont présentes
    required_env_vars = [
        "OPENAI_API_KEY",  # ou autre LLM
        "SERPER_API_KEY",
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  ERREUR: Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("Veuillez créer un fichier .env avec les clés nécessaires.")
        print("Consultez .env.example pour un modèle.")
        return

    # Paramètres d'entrée pour la newsletter
    inputs = {
        "theme": "Intelligence Artificielle et automatisation",
        # Vous pouvez ajouter d'autres paramètres ici selon vos besoins
    }

    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DE LA GÉNÉRATION DE NEWSLETTER")
    print("="*60)
    print(f"📌 Thème: {inputs['theme']}")
    print("="*60 + "\n")

    try:
        # Créer et lancer la crew
        crew = NewsletterMvpCrew()
        result = crew.crew().kickoff(inputs=inputs)

        print("\n" + "="*60)
        print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
        print("="*60)
        print("\n📄 Résultat final:\n")
        print(result)
        print("\n" + "="*60)

        return result

    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERREUR LORS DE LA GÉNÉRATION")
        print("="*60)
        print(f"Erreur: {str(e)}")
        print("="*60 + "\n")
        raise


if __name__ == "__main__":
    main()
