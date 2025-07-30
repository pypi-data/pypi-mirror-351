import requests
import json
import logging
import datetime
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_all_users(maestro_base_url: str, token: str, user_deleting: str):
    """Fetches all users from the specified Maestro base URL.

    Args:
        maestro_base_url (str): The base URL of the Maestro API.
        token (str): The authentication token.
        user_deleting (str): The user performing the deletion action.

    Returns:
        dict: JSON response containing the list of users.
    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors
    """
    headers = {
        "Authorization": token,
        "Dadosfera-User": user_deleting,
        "dadosfera-lang": "pt-br",
    }
    try:
        response = requests.get(f"{maestro_base_url}/users", headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else", err)
    return response.json()


def delete_user(user_id: str, token: str):
    """Deletes a user by their ID.

    Args:
        user_id (str): The ID of the user to be deleted.
        token (str): The authentication token.

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors
    Note:
       - This operation is irreversible - the user cannot be restored after deletion
       - The function logs both the start and completion of the deletion process
    """
    logger.info(f"starting de deletion of the user {user_id}")
    url = f"https://maestro.dadosfera.ai/users/{user_id}"
    headers = {"Authorization": token, "Dadosfera-User": ""}
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else", err)
    logger.info(f"user {user_id} deleted")


def delete_users_from_date(
    maestro_base_url: str, threshold_date_str: str, token: str, user_deleting: str
):
    """Deletes users who haven't logged in after a specified date.
    This is useful for cleaning up stale or abandoned users logins.
    The deletion is permanent and cannot be undone.

    Args:
        maestro_base_url (str): The base URL of the Maestro API.
        threshold_date_str (str): The threshold date in YYYY format.
        token (str): The authentication token.
        user_deleting (str): The user performing the deletion action.

    Raises:
        ValueError: If the threshold_date_str is not in the correct format.

    """
    users = get_all_users(
        maestro_base_url=maestro_base_url, token=token, user_deleting=user_deleting
    )

    try:
        threshold_date = datetime.strptime(threshold_date_str + "-01", "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date format: {threshold_date_str}. Expected format: YYYY"
        )

    for user in users["users"]:
        last_login_date = user.get("lastLogin")
        if not last_login_date or last_login_date < threshold_date:
            delete_user(user_id=user["id"], token=token)
