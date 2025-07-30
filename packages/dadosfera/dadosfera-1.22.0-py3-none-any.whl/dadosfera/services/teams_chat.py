import requests
import logging

logger = logging.getLogger(__name__)

MESSAGE_TEMPLATE = """
{{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "FF0000",
    "summary": "{title}",
    "sections": [
        {{
            "activityTitle": "{title}",
            "text": "{message}"
        }}
    ]
}}
"""


def send_notification(
    teams_webhook_url: str, message_title: str, message_body: str
) -> None:
    """Send a notification message to Microsoft Teams using a webhook URL.

    This function sends a notification message to a Microsoft Teams channel using the Teams webhook API.
    It formats the message using a predefined template and handles the HTTP request and potential errors.

    Args:
        teams_webhook_url (str): The webhook URL for the Microsoft Teams channel.
            Must be a valid URL obtained from Teams channel configuration.
            Example: "https://outlook.office.com/webhook/..."
        message_title (str): The title of the notification message.
            Will be displayed prominently in the Teams notification.
            Should be concise and descriptive.
        message_body (str): The main content of the notification message.
            Can include formatted text according to Teams message card format.
            Will be displayed in the body of the Teams notification.

    Returns:
        None

    Raises:
        requests.exceptions.RequestException: When the HTTP request to Teams webhook fails.
            Contains details about the failure in the exception message.
            Includes response status code and response text in the error log.

    Example:
        >>> webhook_url = "https://outlook.office.com/webhook/..."
        >>> send_notification(
        ...     teams_webhook_url=webhook_url,
        ...     message_title="Deployment Complete",
        ...     message_body="The application was successfully deployed to production."
        ... )

    Notes:
        - The function uses a predefined MESSAGE_TEMPLATE which should follow the Microsoft Teams message card format
        - The webhook URL must be configured in the Teams channel beforehand
        - Network connectivity is required to send notifications
        - The function is synchronous and will block until the request completes

    See Also:
        - Microsoft Teams Webhook Documentation:
          https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
        - Teams Message Card Format:
          https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using#example-of-a-message-card
    """
    headers = {"Content-Type": "application/json"}

    payload = MESSAGE_TEMPLATE.format(title=message_title, message=message_body)

    response = requests.post(teams_webhook_url, headers=headers, data=payload)

    try:
        response.raise_for_status()
        logger.info("Notificação enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Erro ao enviar notificação. Status Code: {response.status_code}, Resposta: {response.text}"
        )
        raise e
