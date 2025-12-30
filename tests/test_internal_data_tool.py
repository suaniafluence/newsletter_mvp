"""
Tests unitaires pour internal_data_tool.py
"""

import unittest
from unittest.mock import patch, mock_open, Mock, MagicMock
import os
import sys
import json
import importlib.util

# Ajouter le chemin source au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock complet des modules crewai avant tout import
def mock_tool_decorator(name):
    """Mock du décorateur @tool qui retourne la fonction sans modification"""
    def decorator(func):
        return func
    return decorator

# Créer des mocks pour tous les modules crewai nécessaires
crewai_mock = MagicMock()
crewai_rag_mock = MagicMock()
crewai_rag_embeddings_mock = MagicMock()
crewai_rag_embeddings_types_mock = MagicMock()
crewai_tools_mock = MagicMock()
crewai_project_mock = MagicMock()

# Configurer le mock du décorateur
crewai_tools_mock.tool = mock_tool_decorator

# Injecter tous les mocks dans sys.modules
sys.modules['crewai'] = crewai_mock
sys.modules['crewai.rag'] = crewai_rag_mock
sys.modules['crewai.rag.embeddings'] = crewai_rag_embeddings_mock
sys.modules['crewai.rag.embeddings.types'] = crewai_rag_embeddings_types_mock
sys.modules['crewai.tools'] = crewai_tools_mock
sys.modules['crewai_tools'] = crewai_tools_mock
sys.modules['crewai.project'] = crewai_project_mock

# Importer directement le module sans passer par __init__.py
spec = importlib.util.spec_from_file_location(
    "internal_data_tool",
    os.path.join(os.path.dirname(__file__), '..', 'src', 'newsletter_mvp', 'tools', 'internal_data_tool.py')
)
internal_data_tool_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(internal_data_tool_module)
load_internal_documents = internal_data_tool_module.load_internal_documents

# Ajouter le module à sys.modules pour que les patches fonctionnent
sys.modules['internal_data_tool'] = internal_data_tool_module


class TestLoadInternalDocuments(unittest.TestCase):
    """Tests pour la fonction load_internal_documents"""

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_success(self, mock_getcwd, mock_file):
        """Test de chargement réussi des documents internes"""
        # Mock du répertoire de travail
        mock_getcwd.return_value = "/fake/path"

        # Mock des données JSON
        test_data = [
            {
                "title": "Document 1",
                "date": "2024-01-01",
                "content": "Contenu du document 1",
                "category": "Catégorie A"
            },
            {
                "title": "Document 2",
                "date": "2024-01-02",
                "content": "Contenu du document 2"
            }
        ]

        # Configurer le mock pour retourner les données JSON
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(test_data)

        # Mock de json.load
        with patch('json.load', return_value=test_data):
            result = load_internal_documents()

        # Vérifications
        self.assertIn("DOCUMENTS INTERNES", result)
        self.assertIn("Document 1", result)
        self.assertIn("Document 2", result)
        self.assertIn("2024-01-01", result)
        self.assertIn("Contenu du document 1", result)
        self.assertIn("Catégorie A", result)

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_with_query(self, mock_getcwd, mock_file):
        """Test de chargement avec un query (même si non utilisé dans la version actuelle)"""
        mock_getcwd.return_value = "/fake/path"

        test_data = [
            {
                "title": "Test Document",
                "date": "2024-01-01",
                "content": "Test content"
            }
        ]

        with patch('json.load', return_value=test_data):
            result = load_internal_documents(query="test")

        # Vérifications - le query n'est pas utilisé mais la fonction devrait fonctionner
        self.assertIn("Test Document", result)

    @patch('internal_data_tool.open')
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_file_not_found(self, mock_getcwd, mock_file):
        """Test de gestion d'erreur lorsque le fichier n'existe pas"""
        mock_getcwd.return_value = "/fake/path"
        mock_file.side_effect = FileNotFoundError("File not found")

        result = load_internal_documents()

        # Vérifications
        self.assertIn("Erreur", result)
        self.assertIn("n'existe pas", result)

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_invalid_json(self, mock_getcwd, mock_file):
        """Test de gestion d'erreur avec JSON mal formaté"""
        mock_getcwd.return_value = "/fake/path"

        # Mock d'un JSON invalide
        with patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            result = load_internal_documents()

        # Vérifications
        self.assertIn("Erreur", result)
        self.assertIn("mal formaté", result)

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_generic_exception(self, mock_getcwd, mock_file):
        """Test de gestion d'erreur générique"""
        mock_getcwd.return_value = "/fake/path"

        # Mock d'une exception générique
        with patch('json.load', side_effect=Exception("Unexpected error")):
            result = load_internal_documents()

        # Vérifications
        self.assertIn("Erreur lors de la lecture", result)
        self.assertIn("Unexpected error", result)

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_empty_list(self, mock_getcwd, mock_file):
        """Test avec une liste vide de documents"""
        mock_getcwd.return_value = "/fake/path"

        test_data = []

        with patch('json.load', return_value=test_data):
            result = load_internal_documents()

        # Vérifications - devrait quand même afficher l'en-tête
        self.assertIn("DOCUMENTS INTERNES", result)

    @patch('internal_data_tool.open', new_callable=mock_open)
    @patch('internal_data_tool.os.getcwd')
    def test_load_internal_documents_missing_fields(self, mock_getcwd, mock_file):
        """Test avec des documents ayant des champs manquants"""
        mock_getcwd.return_value = "/fake/path"

        test_data = [
            {
                # Pas de title, date, ou content
            },
            {
                "title": "Document avec titre seulement"
                # Pas de date ou content
            }
        ]

        with patch('json.load', return_value=test_data):
            result = load_internal_documents()

        # Vérifications - devrait utiliser les valeurs par défaut
        self.assertIn("Sans titre", result)
        self.assertIn("N/A", result)
        self.assertIn("Document avec titre seulement", result)


if __name__ == '__main__':
    unittest.main()
