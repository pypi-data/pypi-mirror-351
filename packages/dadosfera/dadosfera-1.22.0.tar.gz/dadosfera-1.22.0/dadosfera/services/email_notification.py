import logging

from email_sender.email_sender import EmailSender
from email_sender.renders import DictBodyRenderer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


NOTIFICATION_EMAIL_TEMPLATE = """
Alerta: {title}

{message}

Atenciosamente,

Equipe Dadosfera
"""


def send_notification(
    server_smtp, port, from_email, app_password, to_email, subject, message
):
    """
    Sends an email notification via SMTP TLS.

    Parameters:
        server_smtp (str): SMTP server.
        port (int): SMTP server port.
        from_email (str): Sender's email.
        app_password (str): APP password.
        to_email (str or list): Recipient's email(s).
        subject (str): Email subject.
        message (str): Email message body content.
    """
    try:

        renderer = DictBodyRenderer(
            template=NOTIFICATION_EMAIL_TEMPLATE, title=subject, message=message
        )
        body = renderer.render()

        mail_sender = EmailSender(server_smtp, port, from_email, password=app_password)
        message = mail_sender.create_message(to_email, subject, body)

        mail_sender.send_email(to_email, subject, message)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
