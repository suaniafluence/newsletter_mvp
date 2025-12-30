"""
Tests unitaires pour email_sender_tool.py
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
import sys
import smtplib
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
    "email_sender_tool",
    os.path.join(os.path.dirname(__file__), '..', 'src', 'newsletter_mvp', 'tools', 'email_sender_tool.py')
)
email_sender_tool_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(email_sender_tool_module)
send_email = email_sender_tool_module.send_email

# Ajouter le module à sys.modules pour que les patches fonctionnent
sys.modules['email_sender_tool'] = email_sender_tool_module


class TestSendEmail(unittest.TestCase):
    """Tests pour la fonction send_email"""

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': 'recipient1@example.com,recipient2@example.com',
        'NEWSLETTER_SUBJECT': 'Test Newsletter'
    })
    def test_send_email_success(self, mock_smtp_ssl):
        """Test d'envoi d'email réussi"""
        # Mock du serveur SMTP
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        # HTML de test
        test_html = "<html><body><h1>Test Newsletter</h1></body></html>"

        # Appeler la fonction
        result = send_email(test_html)

        # Vérifications
        self.assertIn("Newsletter envoyée avec succès", result)
        self.assertIn("2 destinataire(s)", result)
        self.assertIn("recipient1@example.com", result)
        self.assertIn("recipient2@example.com", result)

        # Vérifier que login a été appelé
        mock_server.login.assert_called_once_with('sender@example.com', 'test_password')

        # Vérifier que sendmail a été appelé
        mock_server.sendmail.assert_called_once()
        call_args = mock_server.sendmail.call_args[0]
        self.assertEqual(call_args[0], 'sender@example.com')
        self.assertEqual(call_args[1], ['recipient1@example.com', 'recipient2@example.com'])

    @patch.dict(os.environ, {}, clear=True)
    def test_send_email_missing_sender(self):
        """Test avec email expéditeur manquant"""
        result = send_email("<html>Test</html>")

        # Vérifications
        self.assertIn("Erreur", result)
        self.assertIn("SMTP_SENDER_EMAIL", result)
        self.assertIn("SMTP_PASSWORD", result)

    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password'
    }, clear=True)
    def test_send_email_missing_recipients(self):
        """Test avec destinataires manquants"""
        result = send_email("<html>Test</html>")

        # Vérifications
        self.assertIn("Erreur", result)
        self.assertIn("SMTP_RECIPIENTS", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'wrong_password',
        'SMTP_RECIPIENTS': 'recipient@example.com'
    })
    def test_send_email_authentication_error(self, mock_smtp_ssl):
        """Test de gestion d'erreur d'authentification"""
        # Mock d'une erreur d'authentification
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Authentication failed')
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        result = send_email("<html>Test</html>")

        # Vérifications
        self.assertIn("Erreur d'authentification SMTP", result)
        self.assertIn("mot de passe d'application", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': 'recipient@example.com'
    })
    def test_send_email_smtp_exception(self, mock_smtp_ssl):
        """Test de gestion d'erreur SMTP générique"""
        # Mock d'une erreur SMTP
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = smtplib.SMTPException("SMTP error occurred")
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        result = send_email("<html>Test</html>")

        # Vérifications
        self.assertIn("Erreur SMTP lors de l'envoi", result)
        self.assertIn("SMTP error occurred", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': 'recipient@example.com'
    })
    def test_send_email_generic_exception(self, mock_smtp_ssl):
        """Test de gestion d'erreur générique"""
        # Mock d'une erreur générique
        mock_smtp_ssl.side_effect = Exception("Unexpected error")

        result = send_email("<html>Test</html>")

        # Vérifications
        self.assertIn("Erreur inattendue lors de l'envoi", result)
        self.assertIn("Unexpected error", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': 'recipient@example.com',
        'SMTP_SERVER': 'custom.smtp.com',
        'SMTP_PORT': '587'
    })
    def test_send_email_custom_smtp_settings(self, mock_smtp_ssl):
        """Test avec paramètres SMTP personnalisés"""
        # Mock du serveur SMTP
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        result = send_email("<html>Test</html>")

        # Vérifier que les paramètres personnalisés ont été utilisés
        mock_smtp_ssl.assert_called_once_with('custom.smtp.com', 587)
        self.assertIn("Newsletter envoyée avec succès", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': 'recipient@example.com'
    })
    def test_send_email_default_subject(self, mock_smtp_ssl):
        """Test avec sujet par défaut"""
        # Mock du serveur SMTP
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        result = send_email("<html>Test</html>")

        # Vérifier que l'email a été envoyé
        self.assertIn("Newsletter envoyée avec succès", result)

    @patch('email_sender_tool.smtplib.SMTP_SSL')
    @patch.dict(os.environ, {
        'SMTP_SENDER_EMAIL': 'sender@example.com',
        'SMTP_PASSWORD': 'test_password',
        'SMTP_RECIPIENTS': '  recipient1@example.com  ,  recipient2@example.com  '
    })
    def test_send_email_recipients_with_whitespace(self, mock_smtp_ssl):
        """Test avec des espaces dans la liste des destinataires"""
        # Mock du serveur SMTP
        mock_server = MagicMock()
        mock_smtp_ssl.return_value.__enter__.return_value = mock_server

        result = send_email("<html>Test</html>")

        # Vérifier que les espaces ont été supprimés
        call_args = mock_server.sendmail.call_args[0]
        self.assertEqual(call_args[1], ['recipient1@example.com', 'recipient2@example.com'])
        self.assertIn("Newsletter envoyée avec succès", result)


if __name__ == '__main__':
    unittest.main()
