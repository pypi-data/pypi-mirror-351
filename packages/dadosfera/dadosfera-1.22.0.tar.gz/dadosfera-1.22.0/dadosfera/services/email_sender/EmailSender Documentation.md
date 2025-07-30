# EmailSender Documentation

## Overview

The `EmailSender` class provides a convenient way to send emails using the Simple Mail Transfer Protocol (SMTP). It allows you to create and send messages, including attachments, from your Python code.

This README explains how to set up and use the `EmailSender` class, including all required and optional parameters, methods, and examples for practical use.

## Features

- Send plain text and HTML emails.

- Add attachments to emails.

- Handle SMTP connections securely.

## Installation

To use the `EmailSender` class, ensure you have Python 3.6+ installed. You also need to install the required libraries:

## Class Overview

EmailSender

The `EmailSender` class is designed to initialize SMTP parameters, create email messages, and send emails with or without attachments.

### Parameters

`smtp_server` (str): The SMTP server address (e.g., smtp.gmail.com).

`port` (int): The port to use for the SMTP server (e.g., 587 for TLS).

`from_email` (str): The sender's email address.

`app_password` (str): The application password for SMTP authentication (used in place of a regular password for security purposes).

### Methods

#### Constructor __init__(smtp_server, port, from_email, password)

Initializes the EmailSender class with SMTP details.

Parameters:

`smtp_server` (str): The SMTP server address.

`port` (int): The port to use for SMTP.

`from_email` (str): Sender's email address.

`password` (str): App password for SMTP authentication.

#### Method create_message(to_email, subject, body, mimetype=MessageMimeType.PLAIN, attachment_path=None)

Creates an email message to be sent.

Parameters:

`to_email` (str or list): Recipient's email address or a list of addresses.

`subject` (str): The subject of the email.

`body` (str): The content of the email.

`mimetype` (MessageMimeType): The MIME type of the body (PLAIN or HTML). Default is PLAIN.

`attachment_path` (str, optional): Path to the attachment file.

Returns: `MIMEMultipart` - The complete email message.

#### Method attach_file(msg, attachment_path)

Attaches a file to the provided email message.

Parameters:

`msg (MIMEMultipart)`: The email message to which the file will be attached.

`attachment_path` (str): Path to the attachment file.

#### Method send_email(to_email, subject, message)

Sends the email using the SMTP server.

Parameters:

`to_email` (str or list): Recipient's email address(es).

`subject` (str): The subject of the email.

`message (MIMEMultipart)`: The email message created using create_message().

### Example Usage

Here's an example of how to use the EmailSender class to send an email with and without an attachment:

```python
from dadosfera.services.email_sender.email_sender import EmailSender

# Initialize the EmailSender class with SMTP details
smtp_server = 'smtp.gmail.com'
port = 587

from_email = 'emailsender@sender.com'
app_password = '123456'
to_email = ['fulano@recipient.com', 'ciclano@recipient.com'] # Can be a single email address as well
subject = 'Test Email'
body = 'This is a test email.'
attachment_path = 'path/to/attachment/file'

email_sender = EmailSender(smtp_server, port, from_email, app_password, False)
email_message = email_sender.create_message(to_email, subject, body, attachment_path=attachment_path)
email_sender.send_email(to_email, subject, email_message)
```

### Error Handling

The EmailSender class includes error handling to ensure proper operation:

- ValueError: Raised if any of the required parameters are not provided during initialization.

- FileNotFoundError: Raised if the provided attachment file path is not valid or the file is not found.

- Exception Handling: General exceptions during the SMTP connection or email sending are logged.

### Notes on Security

Application Passwords: It is recommended to use app-specific passwords for sending emails instead of your primary email password. Set up an application password in your email provider's account settings.

Environment Variables: Store sensitive information like from_email and app_password in environment variables to prevent exposure in your code.

### Testing

Use the provided test_email_sender.py to test the class functionality. The tests cover:

- Email creation with and without attachments.

- Sending emails successfully.

- Handling failed SMTP connections and missing attachments.

To run the tests, use:

```bash
pytest dadosfera/services/email_sender/test_email_sender.py
```

### Troubleshooting

Attachment Issues: Ensure the mimetypes library correctly identifies the file type, or specify the correct type manually if needed.

SMTP Authentication: Ensure that the app_password is correct and that your email provider allows less secure apps or that the necessary permissions are granted.

### License

This project is licensed under the MIT License. See the LICENSE file for more information.
