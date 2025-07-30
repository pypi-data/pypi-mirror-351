import requests
import json
import logging
import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def fetch_catalog_asset_count(
    maestro_base_url: str, token: str, additional_params: Dict[str, str] = {}
) -> int:
    """Fetch the total number of data assets from Maestro.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access.
        additional_params (Dict[str, str], optional): Additional query parameters to include
            in the request. These parameters will override default sorting parameters if
            there are conflicts. Defaults to {}.
    Returns:
        int: Total number of data assets.
    Raises:
        requests.exceptions.HTTPError: If the API request fails with a non-200 status code.
        requests.exceptions.ConnectionError: If there's a network connection error.
        requests.exceptions.Timeout: If the request times out.
        requests.exceptions.RequestException: For any other request-related errors.
    Example:
        >>> assets = fetch_catalog_asset_count(
        ...     maestro_base_url="https://maestro.example.com/api",
        ...     token="bearer_token_123",
        ...     additional_params = {}
        ... )
        >>> logger.info(assets)
        5000
    """
    params = {"size": 1}

    params.update(additional_params)
    try:
        response = requests.get(
            f"{maestro_base_url}/catalog",
            params=params,
            headers={"Content-Type": "application/json", "Authorization": token},
        )
    except requests.exceptions.HTTPError as errh:
            logger.info("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        logger.info("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        logger.info("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        logger.info("OOps: Something Else",err)

    return int(response.json()["total"])


def fetch_paginated_catalog_assets(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
    size: int = 50,
    start_page: int = 1,
) -> List[Dict[str, Any]]:
    """Fetch all data assets from Maestro's catalog using pagination.

    This function retrieves the complete list of data assets by making multiple paginated
    requests to the Maestro catalog API. Assets are sorted by display name in ascending order.
    If the initial request fails, appropriate error messages will be logged.

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
        List[Dict[str, Any]]: List of data asset objects. Each object contains metadata
            about a data asset as returned by the Maestro API.

    Raises:
        requests.exceptions.HTTPError: If the API request fails with a non-200 status code.
        requests.exceptions.ConnectionError: If there's a network connection error.
        requests.exceptions.Timeout: If the request times out.
        requests.exceptions.RequestException: For any other request-related errors.
    Example:
        >>> assets = fetch_paginated_catalog_assets(
        ...     maestro_base_url="https://maestro.example.com/api",
        ...     token="bearer_token_123",
        ...     size=100
        ... )
        >>> logger.info(f"Retrieved {len(assets)} assets")
    """
    num_data_assets = fetch_catalog_asset_count(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params=additional_params,
    )

    logger.info(f"Found {num_data_assets} of this type")

    page = start_page
    data_assets = []
    while len(data_assets) < num_data_assets:
        params = {"size": size, "page": page, "order": "asc", "sort_by": "display_name"}

        params.update(additional_params)
        try:
            response = requests.get(
                f"{maestro_base_url}/catalog",
                headers={"Content-Type": "application/json", "Authorization": token},
                params=params,
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
        response_json = response.json()
        data_assets.extend(response_json["data_assets"])
        logger.info(f"Data assets retrieved: {len(data_assets)}")
        page += 1
    return data_assets



def get_data_asset_table_metadata(
    maestro_base_url: str,
    token: str,
    data_asset_id: str,
    additional_params: Dict[str, str] = {}
) -> Dict[str, Any]:
    """Fetch comprehensive metadata information about a data asset.

    Retrieves detailed metadata about a specific data asset including its general properties,
    schema information, and configuration details.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'catalog:read'
            permission.
        data_asset_id (str): Unique identifier of the data asset
            (e.g., 'asset_abc123').
        additional_params (Dict[str, str], optional): Additional query parameters to include
            in the request.
            Defaults to {}.

    Returns:
        Dict[str, Any]: Data asset metadata including

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
            - 404: Data asset not found
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors

    """
    try:
        response = requests.get(
            f"{maestro_base_url}/catalog/data-asset/{data_asset_id}",
            headers={"Content-Type": "application/json", "Authorization": token},
            params=additional_params,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error fetching data asset metadata: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Connection Error: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Unexpected error fetching data asset metadata: {err}")

def get_data_asset_column_metadata(
    maestro_base_url: str,
    token: str,
    data_asset_id: str,
    additional_params: Dict[str, str] = {}
) -> Dict[str, Any]:
    """Fetch detailed column metadata for a data asset.

    Retrieves comprehensive metadata about all columns in a specific data asset,
    including data types, descriptions, and statistical information when available.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'catalog:read'
            permission.
        data_asset_id (str): Unique identifier of the data asset
            (e.g., 'asset_abc123').
        additional_params (Dict[str, str], optional): Additional query parameters.
            Common parameters include:
            - include_stats: Include statistical information
            - include_samples: Include value samples
            Defaults to {}.

    Returns:
        Dict[str, Any]: Column metadata information including:
            - columns (List[Dict]): List of column definitions

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
            - 404: Data asset not found
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors

    """
    try:
        response = requests.get(
            f"{maestro_base_url}/catalog/data-asset/{data_asset_id}/columns-metadata",
            headers={"Content-Type": "application/json", "Authorization": token},
            params=additional_params,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error fetching column metadata: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Connection Error: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Unexpected error fetching column metadata: {err}")

def get_data_asset_data_preview(
    maestro_base_url: str,
    token: str,
    data_asset_id: str,
    additional_params: Dict[str, str] = {}
) -> Dict[str, Any]:
    """Fetch a data preview for a specific data asset.

    Retrieves a sample of rows from the data asset to preview its content. The preview
    typically includes a limited number of rows and columns for quick inspection.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'catalog:read'
            permission.
        data_asset_id (str): Unique identifier of the data asset
            (e.g., 'asset_abc123').
        additional_params (Dict[str, str], optional): Additional query parameters.
            Common parameters include:
            - limit: Maximum number of rows to return
            - offset: Number of rows to skip
            - columns: Specific columns to include
            Defaults to {}.

    Returns:
        Dict[str, Any]: Preview data

    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
            - 401: Invalid or expired token
            - 403: Insufficient permissions
            - 404: Data asset not found
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors

    """
    try:
        response = requests.get(
            f"{maestro_base_url}/catalog/data-asset/{data_asset_id}/preview",
            headers={"Content-Type": "application/json", "Authorization": token},
            params=additional_params,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error fetching data preview: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Connection Error: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Unexpected error fetching data preview: {err}")

def bulk_delete_data_assets(
    maestro_base_url: str, token: str, additional_params: Dict[str, str]
):
    """Bulk delete data assets based on specified parameters.
    Args:
        maestro_base_url (str): Base URL of the Maestro instance 
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'catalog:read' 
            permission.
        additional_params (Dict[str, str], optional): Additional query parameters.
            Common parameters include:
            - limit: Maximum number of rows to return
            - offset: Number of rows to skip
            - columns: Specific columns to include
            Defaults to {}.
    Note:
       - This operation is irreversible - the data assets cannot be restored after deletion
       - Requires the 'data_assets:delete' permission in the authentication token
       - The function logs both the start and completion of the deletion process
    """
    data_assets = get_data_assets(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params=additional_params,
    )
    for data_asset in data_assets:
        data_asset_id = data_asset["id"]
        delete_data_asset(
            maestro_base_url=maestro_base_url, token=token, data_asset_id=data_asset_id
        )


def delete_data_asset(maestro_base_url: str, token: str, data_asset_id: str):
    """Delete a specified data asset from Maestro.
    Permanently removes a data asset and all its associated configurations from Maestro.
    The operation cannot be undone. Requires appropriate delete permissions.
    Args:
        maestro_base_url (str): Base URL of the Maestro instance 
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access. Must have 'catalog:read' 
            permission.
        data_asset_id (str): Unique identifier of the data asset 
            (e.g., 'asset_abc123').
    Note:
       - This operation is irreversible - the data asset cannot be restored after deletion
       - Requires the 'data_assets:delete' permission in the authentication token
       - The function logs both the start and completion of the deletion process
    """
    logger.info(f"Deleting data_asset: {data_asset_id}")
    response = requests.delete(
        f"{maestro_base_url}/catalog/data-asset/{data_asset_id}",
        headers={"Content-Type": "application/json", "Authorization": token},
    )
    if response.status_code != 200:
        response.raise_for_status()
    logger.info(f"Successfully deleted data_asset: {data_asset_id}")


def get_data_assets(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
    size: int = 50,
    start_page: int = 1,
):
    return fetch_paginated_catalog_assets(maestro_base_url=maestro_base_url, token=token, additional_params=additional_params, size=size, start_page=start_page)

def get_total_data_assets(
    maestro_base_url: str, token: str, additional_params: Dict[str, str] = {}
):
    return fetch_catalog_asset_count(maestro_base_url=maestro_base_url, token=token, additional_params=additional_params)
