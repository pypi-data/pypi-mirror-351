import requests
import json
import logging
import datetime
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_user_config(
    maestro_base_url: str, email: str, password: str, totp: Optional[str] = None
) -> json:
    """Authenticate and retrieve user configuration from Maestro.

    Performs authentication against the Maestro API and returns comprehensive user
    configuration including permissions, tokens, MFA status, terms of use status,
    user details, and customer information.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        email (str): User's email address for authentication.
        password (str): User's password for authentication.
        totp (Optional[str], optional): Time-based One-Time Password for two-factor
            authentication. Required if 2FA is enabled for the user. Defaults to None.

    Returns:
        Dict[str, Any]: User configuration containing:
            - permissions (List[str]): List of user's access permissions
            - tokens (Dict[str, str]): Authentication tokens including:
                - idToken: Identity token
                - accessToken: API access token
                - refreshToken: Token for refreshing access
            - mfaStatus (str): Multi-factor authentication status
            - termsOfUse (Dict): Terms of use acceptance status including:
                - status (str): Current status
                - lastSigned (Dict): Details of last terms acceptance
                    - version (int): Terms version number
                    - publicUrl (str): URL to terms document
                    - enforceDate (str): Enforcement date
                    - createdAt (str): Creation timestamp
            - user (Dict): User profile information:
                - id (str): Unique user identifier
                - name (str): Full name
                - username (str): Username
                - createdAt (str): Account creation timestamp
            - customer (Dict): Customer account details:
                - modules (List[str]): Enabled product modules
                - links (List[Dict]): Custom dashboard links
                - id (str): Customer account ID
                - name (str): Customer account name
                - tier (str): Subscription tier
                - scheduleLimit (str): Pipeline schedule frequency limit

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
                - 401: Invalid or expired token
                - 403: Insufficient permissions
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors
        ValueError: If provided credentials are invalid
        AuthenticationError: If authentication fails (invalid email/password/TOTP)

    Example:
        >>> config = get_user_config(
        ...     maestro_base_url="https://maestro.example.com/api",
        ...     email="user@example.com",
        ...     password="secure_password"
        ... )
        >>> # Check user permissions
        >>> if "catalog:edit" in config["permissions"]:
        ...     logger.info("User can edit catalog")
        User can edit catalog
        >>>
        >>> # Access API token
        >>> token = config["tokens"]["accessToken"]
        >>> logger.info(f"Token: {token[:10]}...")
        Token: random-tok...
        >>>
        >>> # Get customer tier
        >>> logger.info(f"Account tier: {config['customer']['tier']}")
        Account tier: STANDARD
    """
    data = {"username": email, "password": password, "totp": totp}
    try:
        response = requests.post(
            f"{maestro_base_url}/auth/sign-in",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else",err)
    return response.json()


def get_token(
    maestro_base_url: str, email: str, password: str, totp: Optional[str] = None
) -> str:
    """Authenticate with Maestro using given credentials and return the authentication token.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        email (str): User's email address for authentication.
        password (str): User's password for authentication.
        totp (Optional[str], optional): Time-based One-Time Password for two-factor
            authentication. Required if 2FA is enabled for the user. Defaults to None.


    Returns:
        token (str): Authentication token for API access.
    Example:
        >>> token = get_token(
        ...     maestro_base_url="https://maestro.example.com/api",
        ...     email="user@example.com",
        ...     password="secure_password"
        ... )
        >>> logger.info(f"Token: {token[:10]}...")
        Token: random-tok...

    """
    user_config = get_user_config(
        maestro_base_url=maestro_base_url, email=email, password=password
    )
    return user_config["tokens"]["accessToken"]
