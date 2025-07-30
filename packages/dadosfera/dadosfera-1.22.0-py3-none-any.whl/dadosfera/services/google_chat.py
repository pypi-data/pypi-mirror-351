from email import message
import requests
import logging
import json

logger = logging.getLogger(__name__)


MESSAGE_TEMPLATE = {
    "cards": [
        {
            "header": {"title": ""},
            "sections": [{"widgets": [{"textParagraph": {"text": ""}}]}],
        }
    ]
}


def send_notification(url: str, title: str, message: str, link: str = None) -> None:
    """Send a notification message to Google Chat using a webhook URL, with a title, message, and optional link.

    This function sends a notification message to a Google Chat channel using the Google Chat webhook API.
    It formats the message using a predefined template and handles the HTTP request and potential errors.

    Args:
        url (str): The webhook URL for the Google Chat channel.
            Must be a valid URL obtained from Google Chat channel configuration.
            Example: "https://chat.googleapis.com/v1/spaces/AAAAA_BBBBB/messages?key=xyz..."

        title (str): The title of the notification message.
            Should be concise and descriptive.
            Will be displayed prominently in the message card.
            Example: "Deployment Status" or "Alert: System Error"

        message (str): The main content of the notification message.
            Can include formatted text according to Google Chat message card format.
            Will be displayed in the body of the Google Chat notification.
            Example: "The deployment to production was successful." or "CPU usage above 90%"

        link (str, optional): A URL to be included in the notification message as a clickable button.
            If provided, a button labeled will be added to the message card.
            If not provided, the message will be sent without a button.
            Example: "https://example.com/progress-tracker"

    Returns:
        None: The function returns nothing on success.
            Raises an exception on failure.

    Raises:
        requests.exceptions.RequestException: When the HTTP request to Google Chat webhook fails.
            Common failure cases:
            - Invalid webhook URL
            - Network connectivity issues
            - Rate limiting
            - Server errors
            The exception includes:
            - Response status code
            - Response body
            - Original error message

    Example:
        >>> webhook_url = "https://chat.googleapis.com/v1/spaces/..."
        >>> try:
        ...     send_notification(
        ...         url=webhook_url,
        ...         title="Deployment Complete",
        ...         message="Successfully deployed version 1.2.3 to production",
        ...         link="https://example.com/progress"
        ...     )
        ... except requests.exceptions.RequestException as e:
        ...     print(f"Failed to send notification: {e}")

    Notes:
        - The function uses a predefined MESSAGE_TEMPLATE which should follow the Google Chat message card format.
        - If a `link` is provided, it will be rendered as a clickable button in the card.
        - Network connectivity is required to send notifications
        - The function is synchronous and will block until the request completes
        - Messages are sent with UTF-8 encoding

    Dependencies:
        - requests: For making HTTP requests
        - logging: For operation logging
        - MESSAGE_TEMPLATE: Global constant with message template

    See Also:
        - Google Chat Webhook Documentation:
          https://developers.google.com/chat/how-tos/webhooks
        - Message Card Format Reference:
          https://developers.google.com/chat/api/reference/rest/v1/spaces.messages
    """
    headers = {"Content-Type": "application/json; charset=UTF-8"}

    payload = MESSAGE_TEMPLATE.copy()
    payload["cards"][0]["header"]["title"] = title
    payload["cards"][0]["sections"][0]["widgets"][0]["textParagraph"]["text"] = message

    if link:
        button_widget = {
            "buttons": [
                {
                    "textButton": {
                        "text": "CLIQUE PARA MAIS DETALHES",
                        "onClick": {"openLink": {"url": link}},
                    }
                }
            ]
        }
        payload["cards"][0]["sections"][0]["widgets"].append(button_widget)

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        response.raise_for_status()
        logger.info("Notificação enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        logger.error("Erro ao enviar notificação")
        raise e
