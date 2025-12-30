"""
Tool d'envoi d'emails
Permet d'envoyer les newsletters par email via SMTP (Gmail).
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai_tools import tool


@tool("email_sender_tool")
def send_email(newsletter_html: str) -> str:
    """
    Envoie la newsletter par email via SMTP Gmail.

    Args:
        newsletter_html: Le contenu HTML de la newsletter à envoyer

    Returns:
        Message de confirmation ou d'erreur
    """
    # Récupérer les paramètres depuis les variables d'environnement
    sender = os.getenv("SMTP_SENDER_EMAIL")
    password = os.getenv("SMTP_PASSWORD")
    recipients_str = os.getenv("SMTP_RECIPIENTS", "")

    # Validation des paramètres
    if not sender or not password:
        return "Erreur: SMTP_SENDER_EMAIL et SMTP_PASSWORD doivent être définis dans les variables d'environnement"

    if not recipients_str:
        return "Erreur: SMTP_RECIPIENTS doit être défini (emails séparés par des virgules)"

    # Parser la liste des destinataires
    recipients = [email.strip() for email in recipients_str.split(",")]

    try:
        # Créer le message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = os.getenv("NEWSLETTER_SUBJECT", "Newsletter Automatique")
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        # Ajouter le contenu HTML
        part = MIMEText(newsletter_html, "html", "utf-8")
        msg.attach(part)

        # Connexion et envoi via Gmail SMTP
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "465"))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())

        return f"Newsletter envoyée avec succès à {len(recipients)} destinataire(s): {', '.join(recipients)}"

    except smtplib.SMTPAuthenticationError:
        return "Erreur d'authentification SMTP. Vérifiez vos identifiants et assurez-vous d'utiliser un mot de passe d'application Gmail."
    except smtplib.SMTPException as e:
        return f"Erreur SMTP lors de l'envoi: {str(e)}"
    except Exception as e:
        return f"Erreur inattendue lors de l'envoi: {str(e)}"
