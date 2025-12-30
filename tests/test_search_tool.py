"""
Tests unitaires pour search_tool.py
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys
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
    "search_tool",
    os.path.join(os.path.dirname(__file__), '..', 'src', 'newsletter_mvp', 'tools', 'search_tool.py')
)
search_tool_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search_tool_module)
search_articles = search_tool_module.search_articles

# Ajouter le module à sys.modules pour que les patches fonctionnent
sys.modules['search_tool'] = search_tool_module


class TestSearchArticles(unittest.TestCase):
    """Tests pour la fonction search_articles"""

    @patch('search_tool.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_articles_success(self, mock_post):
        """Test de recherche réussie avec des résultats"""
        # Mock de la réponse de l'API
        mock_response = Mock()
        mock_response.json.return_value = {
            'organic': [
                {
                    'title': 'Article 1',
                    'link': 'https://example.com/article1',
                    'snippet': 'Ceci est un extrait de l\'article 1'
                },
                {
                    'title': 'Article 2',
                    'link': 'https://example.com/article2',
                    'snippet': 'Ceci est un extrait de l\'article 2'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Appeler la fonction
        result = search_articles("Intelligence Artificielle")

        # Vérifications
        self.assertIn("Article 1", result)
        self.assertIn("Article 2", result)
        self.assertIn("https://example.com/article1", result)
        self.assertIn("extrait de l'article 1", result)

        # Vérifier que l'API a été appelée correctement
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['q'], "Intelligence Artificielle")

    @patch('search_tool.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_articles_no_results(self, mock_post):
        """Test de recherche sans résultats"""
        # Mock de la réponse sans résultats
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Appeler la fonction
        result = search_articles("TopicWithNoResults")

        # Vérifications
        self.assertIn("Aucun résultat trouvé", result)

    @patch.dict(os.environ, {}, clear=True)
    def test_search_articles_missing_api_key(self):
        """Test avec clé API manquante"""
        result = search_articles("Test Topic")

        # Vérifications
        self.assertIn("Erreur", result)
        self.assertIn("SERPER_API_KEY", result)

    @patch('search_tool.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_articles_request_exception(self, mock_post):
        """Test de gestion d'erreur de requête"""
        # Mock d'une exception lors de la requête
        mock_post.side_effect = Exception("Network error")

        # Appeler la fonction
        result = search_articles("Test Topic")

        # Vérifications
        self.assertIn("Erreur inattendue", result)
        self.assertIn("Network error", result)

    @patch('search_tool.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_articles_http_error(self, mock_post):
        """Test de gestion d'erreur HTTP"""
        # Mock d'une erreur HTTP
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        # Appeler la fonction
        result = search_articles("Test Topic")

        # Vérifications
        self.assertIn("Erreur lors de la recherche web", result)

    @patch('search_tool.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_articles_limits_to_10_results(self, mock_post):
        """Test que la fonction limite les résultats à 10"""
        # Mock avec plus de 10 résultats
        mock_response = Mock()
        organic_results = [
            {
                'title': f'Article {i}',
                'link': f'https://example.com/article{i}',
                'snippet': f'Snippet {i}'
            }
            for i in range(1, 16)  # 15 résultats
        ]
        mock_response.json.return_value = {'organic': organic_results}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Appeler la fonction
        result = search_articles("Test Topic")

        # Vérifier que seulement 10 résultats sont inclus
        for i in range(1, 11):
            self.assertIn(f"Article {i}", result)
        # Le 11ème ne devrait pas être là
        self.assertNotIn("Article 11", result)


if __name__ == '__main__':
    unittest.main()
