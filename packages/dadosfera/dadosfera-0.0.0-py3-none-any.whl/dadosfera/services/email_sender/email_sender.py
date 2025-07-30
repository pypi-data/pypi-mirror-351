import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from enum import Enum
import mimetypes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageMimeType(Enum):
    PLAIN = "plain"
    HTML = "html"


class EmailSender:
    """
    Initializes the EmailSender class.

    Parameters:
        smtp_server (str): SMTP server.
        port (int): SMTP server port.
        from_email (str): Sender's email.
        app_password (str): APP password to SMTP authenticate.
    """
    def __init__(self, smtp_server, port, from_email, password, use_ssl=False):
        self.smtp_server = smtp_server
        self.port = port
        self.from_email = from_email
        self.app_password = password
        self.use_ssl = use_ssl

        # Validate parameters to avoid runtime errors
        if not all([smtp_server, port, from_email, password]):
            raise ValueError("Please provide all parameters, they are mandatory.")


    def create_message(self, to_email, subject, body, mimetype=MessageMimeType.PLAIN, attachment_path=None):
        """
        Creates an email message.

        Parameters:
            to_email (str or list): Recipient's email(s).
            subject (str): Email subject.
            body (str): Email message body content.
            mimetype (str): Email message body content type (default 'plain').
            attachment_path (str): Path to the attachment file.
        Returns:
            MIMEMultipart: Email message created.
        """
        if isinstance(to_email, str):
            to_email = [to_email]

        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = ', '.join(to_email)
        message["Subject"] = subject
        message.attach(MIMEText(body, mimetype.value))

        if attachment_path:
            self.attach_file(message, attachment_path)

        return message

    def attach_file(self, msg, attachment_path):
        """
        Attaches a file to the email message.

        Parameters:
            msg (MIMEMultipart): Email message.
            attachment_path (str): Path to the attachment file.
        """
        if attachment_path and os.path.isfile(attachment_path):
            try:
                # Guess the MIME type of the attachment file based on its extension
                mime_type, _ = mimetypes.guess_type(attachment_path)
                if mime_type is None:
                    mime_type = "application/octet-stream" # Default MIME type

                # Split the MIME type into main and sub types
                main_type, sub_type = mime_type.split("/", 1)

                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename= "{os.path.basename(attachment_path)}"'
                    )
                    msg.attach(part)
            except Exception as e:
                logger.error(f"Error attaching file: {e}")
                raise e
        else:
            logger.error(f"Attachment file not found: {attachment_path}")
            raise FileNotFoundError(f"Attachment file not found: {attachment_path}")


    def send_email(self, to_email, message):
        """
        Sends an email message using SMTP server.

        Parameters:
            to_email (str or list): Recipient's email(s).
            message (MIMEMultipart): Email message.
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.port)
            if self.use_ssl:
                server.starttls()

            server.login(self.from_email, self.app_password)
            server.sendmail(self.from_email, to_email, message.as_string())
            logger.info(f"Email(s) sent successfully!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            server.quit()
