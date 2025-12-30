# Newsletter MVP - Génération Automatique avec CrewAI

Système de génération automatique de newsletters personnalisées utilisant CrewAI et des agents d'IA collaboratifs.

## Description

Ce projet implémente un système multi-agents capable de :
- Collecter des informations depuis le web (via Serper.dev)
- Extraire des données internes de l'entreprise
- Résumer et analyser les contenus
- Planifier la structure éditoriale
- Rédiger une newsletter complète
- Valider et corriger le contenu
- Personnaliser selon différents segments
- Envoyer par email (via SMTP)

## Architecture

### 8 Agents Spécialisés

1. **Collecteur Externe** - Recherche web d'actualités
2. **Collecteur Interne** - Lecture des données internes
3. **Résumeur** - Synthèse des contenus
4. **Planificateur** - Structure éditoriale
5. **Rédacteur** - Écriture de la newsletter
6. **Validateur** - Relecture et correction
7. **Personnaliseur** - Adaptation par segment
8. **Diffuseur** - Envoi par email

### Structure du Projet

```
newsletter_mvp/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── data/
│   └── internal_docs.json      # Données internes mockées
├── src/
│   └── newsletter_mvp/
│       ├── __init__.py
│       ├── main.py             # Point d'entrée
│       ├── crew.py             # Définition de la crew
│       ├── config/
│       │   ├── agents.yaml     # Configuration des agents
│       │   └── tasks.yaml      # Configuration des tâches
│       └── tools/
│           ├── __init__.py
│           ├── search_tool.py          # Recherche web (Serper)
│           ├── internal_data_tool.py   # Lecture données internes
│           └── email_sender_tool.py    # Envoi emails (SMTP)
```

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone <votre-repo>
cd newsletter_mvp
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**

```bash
pip install -e .
```

## Configuration

### 1. Créer le fichier .env

Copiez `.env.example` vers `.env` et remplissez vos clés API :

```bash
cp .env.example .env
```

### 2. Obtenir les clés API nécessaires

#### OpenAI API Key
- Créez un compte sur [OpenAI](https://platform.openai.com/)
- Générez une clé API dans [API Keys](https://platform.openai.com/api-keys)
- Ajoutez-la dans `.env` : `OPENAI_API_KEY=sk-...`

#### Serper.dev API Key
- Créez un compte gratuit sur [Serper.dev](https://serper.dev)
- Obtenez votre clé API (2500 requêtes gratuites/mois)
- Ajoutez-la dans `.env` : `SERPER_API_KEY=...`

#### Configuration Gmail pour l'envoi d'emails

1. **Activer la validation en 2 étapes** sur votre compte Gmail
2. **Créer un mot de passe d'application** :
   - Allez sur [Mots de passe d'application](https://myaccount.google.com/apppasswords)
   - Sélectionnez "Autre" comme application
   - Copiez le mot de passe généré
3. **Configurez dans `.env`** :
   ```
   SMTP_SENDER_EMAIL=votre.email@gmail.com
   SMTP_PASSWORD=votre-mot-de-passe-application
   SMTP_RECIPIENTS=destinataire@example.com
   ```

### 3. Personnaliser les données internes (optionnel)

Modifiez `data/internal_docs.json` avec vos propres données internes :

```json
[
  {
    "title": "Votre titre",
    "content": "Votre contenu",
    "date": "2025-12-30",
    "category": "Votre catégorie"
  }
]
```

## Utilisation

### Lancer la génération de newsletter

```bash
python src/newsletter_mvp/main.py
```

Ou si vous avez installé le package :

```bash
newsletter-mvp
```

### Personnaliser le thème

Éditez `src/newsletter_mvp/main.py` et modifiez la variable `inputs` :

```python
inputs = {
    "theme": "Votre thème personnalisé",
}
```

### Mode développement

Pour voir les détails d'exécution, activez le mode verbose dans `.env` :

```
CREWAI_VERBOSE=true
```

## Workflow du Système

1. **Collecte Web** : Recherche d'articles récents sur le thème
2. **Collecte Interne** : Extraction des données internes pertinentes
3. **Résumé** : Synthèse des contenus collectés
4. **Planification** : Création du plan éditorial
5. **Rédaction** : Écriture de la newsletter
6. **Validation** : Relecture et correction
7. **Personnalisation** : Adaptation par segment client
8. **Diffusion** : Envoi par email

## Personnalisation

### Ajouter un nouvel agent

1. Éditez `src/newsletter_mvp/config/agents.yaml`
2. Ajoutez la définition dans `src/newsletter_mvp/crew.py`
3. Créez la tâche correspondante dans `tasks.yaml`

### Créer un nouveau tool

1. Créez un fichier dans `src/newsletter_mvp/tools/`
2. Utilisez le décorateur `@tool`
3. Importez-le dans `crew.py`
4. Assignez-le à un agent

Exemple :

```python
from crewai_tools import tool

@tool("my_custom_tool")
def my_tool(input: str) -> str:
    """Description de votre outil"""
    # Votre logique ici
    return result
```

## Tests

Pour tester sans envoyer d'emails, commentez l'appel à `send_email` dans le workflow ou modifiez `SMTP_RECIPIENTS` avec un email de test.

## Dépannage

### Erreur "OPENAI_API_KEY not found"
- Vérifiez que `.env` existe et contient `OPENAI_API_KEY`
- Vérifiez que `python-dotenv` est installé

### Erreur d'authentification SMTP
- Utilisez un **mot de passe d'application** Gmail, pas votre mot de passe normal
- Activez la validation en 2 étapes sur Gmail
- Vérifiez que SMTP_PORT=465 (SSL)

### Erreur Serper API
- Vérifiez votre quota (2500 requêtes gratuites/mois)
- Vérifiez la validité de votre clé API

## Évolutions Futures

- [ ] Support de multiples providers LLM (Anthropic, Groq, etc.)
- [ ] Interface web pour configuration
- [ ] Planification automatique (cron jobs)
- [ ] Métriques et analytics
- [ ] A/B testing des contenus
- [ ] Base de données pour historique
- [ ] API REST pour intégration

## Licence

MIT

## Support

Pour toute question ou problème, ouvrez une issue sur le dépôt GitHub.

---

**Note** : Ce projet est un MVP (Minimum Viable Product). Il est conçu pour être étendu et personnalisé selon vos besoins spécifiques.
