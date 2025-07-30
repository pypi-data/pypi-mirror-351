import requests
import json
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dateutil.parser import parse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def fetch_paginated_connections(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
) -> List[Dict]:
    """
    Fetch connections from Maestro with pagination..

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access.
        additional_params (Dict[str, str], optional): Additional query parameters to include
            in the request. These parameters will override default sorting parameters if
            there are conflicts. Defaults to {}.
        size (int, optional): Number of data assets to fetch per page. A larger size means
            fewer API calls but more data per request. Defaults to 50.
        start_page (int, optional): Page number to start fetching from. Useful for resuming
            interrupted fetches. Defaults to 1.


    Returns:
        List[Dict]: List of connections.

    Raises:
        ValueError: If `size` or `start_page` is less than or equal to zero.
        requests.exceptions.HTTPError: For failed API requests. Common cases:
           - 401: Invalid or expired token
           - 403: Insufficient permissions
           - 404: Connection ID not found
       requests.exceptions.ConnectionError: For network connectivity issues
       requests.exceptions.Timeout: For request timeouts
       requests.exceptions.RequestException: For other request-related errors
    """

    # Validate input parameters
    if additional_params["size"] and additional_params["size"] <= 0:
        raise ValueError("Size must be greater than zero.")
    if additional_params["start_page"] and additional_params["start_page"] <= 0:
        raise ValueError("Start page must be greater than zero.")

    connections = []
    params = {}
    params.update(additional_params)

    try:
        response = requests.get(
            f"{maestro_base_url}/connections",
            headers={"Content-Type": "application/json", "Authorization": token},
            params=params,
        )
        response.raise_for_status()
        response_json = response.json()

    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else", err)

    connections = response_json.get("connections", [])
    logger.info(f"Connections retrieved: {len(connections)}")
    return connections


def delete_connection(maestro_base_url: str, token: str, connection_id: str) -> None:
    """Delete a data connection from the Maestro platform.

    Permanently removes a data connection and all its associated configurations from Maestro.
    The operation cannot be undone. Requires appropriate delete permissions.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'connection:delete'
            permission.
        connection_id (str): Unique identifier of the connection to be deleted
            (e.g., 'conn_abc123').

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
            - 404: Connection ID not found
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors

      ## Example
      ### Delete a database connection:
     ```python
     try:
         delete_connection(
             maestro_base_url="https://maestro.example.com/api",
             token="bearer_token_123",
             connection_id="conn_abc123"
         )
         logger.info("Connection deleted successfully")
     except requests.exceptions.HTTPError as e:
         if e.response.status_code == 414:
             logger.info("Connection not found")
         elif e.response.status_code == 403:
             logger.info("Permission denied")
         else:
             raise
         'Connection deleted successfully'
     ```

    Note:
        - This operation is irreversible - the connection cannot be restored after deletion
        - Any pipelines or transformations using this connection will need to be updated
        - Requires the 'connection:delete' permission in the authentication token
        - The function logs both the start and completion of the deletion process
    """

    logger.info(f"Deleting connection: {connection_id}")
    try:
        response = requests.delete(
            f"{maestro_base_url}/connections/{connection_id}",
            headers={"Content-Type": "application/json", "Authorization": token},
        )

        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.info("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else", err)
    logger.info(f"Successfully deleted connection: {connection_id}")


def delete_inactive_connections(
    maestro_base_url: str, token: str, additional_params: Dict[str, str] = {}
):
    """Bulk delete inactive connections from Maestro.
    Deletes multiple connections that match the specified criteria and haven't been updated
    in the last 60 days. This is useful for cleaning up stale or abandoned connections.
    The deletion is permanent and cannot be undone.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'connection:delete'
            permission.
        additional_params (Dict[str, str], optional): Filtering parameters to specify which
            connections to consider for deletion. Common filters include:
            - type: Connection type (e.g., 'postgres', 'snowflake')
            - status: Connection status (e.g., 'active', 'inactive')
            - name: Connection name pattern
            Defaults to {}.

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts

        ValueError: If date parsing fails for connection timestamps
    """

    connections = fetch_paginated_connections(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params=additional_params,
    )

    two_months_ago = datetime.strptime(
        (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"), "%Y-%m-%d"
    )

    for connection in connections:
        connection_id = connection["id"]
        updated_at = datetime.strptime(
            parse(connection["updated_at"]).strftime("%Y-%m-%d"), "%Y-%m-%d"
        )

        if updated_at < two_months_ago:
            delete_connection(
                maestro_base_url=maestro_base_url,
                token=token,
                connection_id=connection_id,
            )


def get_connections(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
):
    return fetch_paginated_connections(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params=additional_params,
    )


def bulk_delete_connections(
    maestro_base_url: str, token: str, additional_params: Dict[str, str] = {}
):
    return delete_inactive_connections(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params=additional_params,
    )
