"""
Tests unitaires pour main.py
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys

# Mock des modules crewai avant l'import pour éviter les erreurs de dépendances
# Le décorateur tool doit être une fonction qui retourne la fonction sans modification
def mock_tool_decorator(name):
    def decorator(func):
        return func
    return decorator

crewai_mock = MagicMock()
crewai_tools_mock = MagicMock()
crewai_project_mock = MagicMock()
crewai_tools_mock.tool = mock_tool_decorator
sys.modules['crewai'] = crewai_mock
sys.modules['crewai.tools'] = crewai_tools_mock
sys.modules['crewai_tools'] = crewai_tools_mock
sys.modules['crewai.project'] = crewai_project_mock

# Ajouter le chemin source au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from newsletter_mvp.main import main


class TestMain(unittest.TestCase):
    """Tests pour la fonction main"""

    @patch('newsletter_mvp.main.NewsletterMvpCrew')
    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'SERPER_API_KEY': 'test_serper_key'
    })
    def test_main_success(self, mock_load_dotenv, mock_crew_class):
        """Test de l'exécution réussie de main()"""
        # Mock de la crew et de son résultat
        mock_crew_instance = MagicMock()
        mock_crew_result = MagicMock()
        mock_crew_result.__str__ = Mock(return_value="Newsletter générée avec succès")
        mock_crew_instance.crew.return_value.kickoff.return_value = mock_crew_result
        mock_crew_class.return_value = mock_crew_instance

        # Capturer la sortie
        with patch('builtins.print') as mock_print:
            result = main()

        # Vérifications
        mock_load_dotenv.assert_called_once()
        mock_crew_class.assert_called_once()
        mock_crew_instance.crew.return_value.kickoff.assert_called_once()

        # Vérifier que le résultat a été retourné
        self.assertEqual(result, mock_crew_result)

        # Vérifier que des messages ont été affichés
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("DÉMARRAGE" in str(call) for call in print_calls))
        self.assertTrue(any("SUCCÈS" in str(call) for call in print_calls))

    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_missing_openai_key(self, mock_load_dotenv):
        """Test avec clé OPENAI_API_KEY manquante"""
        with patch('builtins.print') as mock_print:
            result = main()

        # Vérifications
        self.assertIsNone(result)

        # Vérifier que le message d'erreur a été affiché
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("ERREUR" in str(call) for call in print_calls))
        self.assertTrue(any("OPENAI_API_KEY" in str(call) for call in print_calls))

    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}, clear=True)
    def test_main_missing_serper_key(self, mock_load_dotenv):
        """Test avec clé SERPER_API_KEY manquante"""
        with patch('builtins.print') as mock_print:
            result = main()

        # Vérifications
        self.assertIsNone(result)

        # Vérifier que le message d'erreur a été affiché
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("ERREUR" in str(call) for call in print_calls))
        self.assertTrue(any("SERPER_API_KEY" in str(call) for call in print_calls))

    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_missing_all_keys(self, mock_load_dotenv):
        """Test avec toutes les clés manquantes"""
        with patch('builtins.print') as mock_print:
            result = main()

        # Vérifications
        self.assertIsNone(result)

        # Vérifier que le message d'erreur a été affiché
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("OPENAI_API_KEY" in str(call) and "SERPER_API_KEY" in str(call)
                           for call in print_calls))

    @patch('newsletter_mvp.main.NewsletterMvpCrew')
    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'SERPER_API_KEY': 'test_serper_key'
    })
    def test_main_crew_exception(self, mock_load_dotenv, mock_crew_class):
        """Test de gestion d'erreur lors de l'exécution de la crew"""
        # Mock d'une exception lors de l'exécution
        mock_crew_instance = MagicMock()
        mock_crew_instance.crew.return_value.kickoff.side_effect = Exception("Crew execution failed")
        mock_crew_class.return_value = mock_crew_instance

        # Vérifier que l'exception est propagée
        with self.assertRaises(Exception) as context:
            with patch('builtins.print'):
                main()

        self.assertIn("Crew execution failed", str(context.exception))

    @patch('newsletter_mvp.main.NewsletterMvpCrew')
    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'SERPER_API_KEY': 'test_serper_key'
    })
    def test_main_inputs_passed_correctly(self, mock_load_dotenv, mock_crew_class):
        """Test que les inputs sont passés correctement à la crew"""
        # Mock de la crew
        mock_crew_instance = MagicMock()
        mock_crew_result = MagicMock()
        mock_crew_instance.crew.return_value.kickoff.return_value = mock_crew_result
        mock_crew_class.return_value = mock_crew_instance

        with patch('builtins.print'):
            main()

        # Vérifier que kickoff a été appelé avec les bons inputs
        call_args = mock_crew_instance.crew.return_value.kickoff.call_args
        self.assertIn('inputs', call_args[1])
        self.assertIn('theme', call_args[1]['inputs'])
        self.assertEqual(call_args[1]['inputs']['theme'], "Intelligence Artificielle et automatisation")

    @patch('newsletter_mvp.main.NewsletterMvpCrew')
    @patch('newsletter_mvp.main.load_dotenv')
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'SERPER_API_KEY': 'test_serper_key'
    })
    def test_main_error_message_displayed(self, mock_load_dotenv, mock_crew_class):
        """Test que le message d'erreur est affiché correctement"""
        # Mock d'une exception
        mock_crew_instance = MagicMock()
        mock_crew_instance.crew.return_value.kickoff.side_effect = ValueError("Invalid configuration")
        mock_crew_class.return_value = mock_crew_instance

        with patch('builtins.print') as mock_print:
            with self.assertRaises(ValueError):
                main()

        # Vérifier que le message d'erreur a été affiché
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("ERREUR LORS DE LA GÉNÉRATION" in str(call) for call in print_calls))
        self.assertTrue(any("Invalid configuration" in str(call) for call in print_calls))


if __name__ == '__main__':
    unittest.main()
