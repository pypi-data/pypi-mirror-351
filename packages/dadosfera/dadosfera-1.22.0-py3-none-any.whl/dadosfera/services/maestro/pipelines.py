import requests
import json
import logging
import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def fetch_paginated_pipelines(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
    size: int = 500,
    start_page: int = 1,
):
    """Fetch pipelines from Maestro with pagination.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance.
        token (str): Authentication token.
        additional_params (Dict[str, str], optional): Additional parameters to be passed in
          the request. Defaults to {}.
        size (int, optional): Number of pipelines to fetch per request. Defaults to 500.
        start_page (int, optional): Starting page number. Defaults to 1.

    Returns:
        List[Dict]: List of pipelines.

    """
    params = {
        "size": size,
        "page": start_page,
        "order": "asc",
        "sort_by": "display_name",
    }
    params.update(additional_params)
    try:
        response = requests.get(
            f"{maestro_base_url}/pipelinesv2",
            headers={"Content-Type": "application/json", "Authorization": token},
            params=params,
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
    response_json = response.json()
    return response_json["pipelines"]


def fetch_pipeline_execution_history(
    maestro_base_url: str, token: str, pipeline_id: str
) -> List[Dict[str, Any]]:
    """Fetch the execution history and status records for a specific pipeline.

    Retrieves a list of historical execution records including status, timestamps,
    and other metadata for each pipeline run.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access.
        pipeline_id (str): Unique identifier of the pipeline.

    Returns:
        List[Dict[str, Any]]: List of execution records, each containing:
            - status: Current status of the run


    Raises:
        requests.exceptions.HTTPError: For failed API requests. Common cases:
                - 401: Invalid or expired token
                - 403: Insufficient permissions
        requests.exceptions.ConnectionError: For network connectivity issues
        requests.exceptions.Timeout: For request timeouts
        requests.exceptions.RequestException: For other request-related errors
    """
    try:
        response = requests.get(
            f"{maestro_base_url}/pipelinesv2/{pipeline_id}/status",
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

    response_json = response.json()
    return response_json["status"]


def fetch_execution_history_all_pipelines(
    maestro_base_url: str, token: str
) -> List[Dict]:
    """Fetch the execution history and status records for all pipelines.

    Retrieves a list of historical execution records including status, timestamps,
    and other metadata for each pipeline run.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access.

    Returns:
        List[Dict]: List of pipelines execution history.

    """
    all_pipelines = fetch_paginated_pipelines(
        maestro_base_url=maestro_base_url, token=token
    )
    pipeline_ids = [pipeline["id"] for pipeline in all_pipelines]

    execution_history_all_pipelines = []
    for pipeline_id in pipeline_ids:
        pipelines_runs_by_pipeline = fetch_pipeline_execution_history(
            maestro_base_url=maestro_base_url, token=token, pipeline_id=pipeline_id
        )

        execution_history_all_pipelines.extend(pipelines_runs_by_pipeline)

    return execution_history_all_pipelines


def get_pipelines(
    maestro_base_url: str,
    token: str,
    additional_params: Dict[str, str] = {},
    size: int = 500,
    start_page: int = 1,
):

    return fetch_paginated_pipelines(
        maestro_base_url, token, additional_params, size, start_page
    )


def get_status_by_pipeline(maestro_base_url: str, token: str, pipeline_id: str):
    return fetch_pipeline_execution_history(maestro_base_url, token, pipeline_id)


def get_status_of_all_pipelines(maestro_base_url: str, token: str):
    return fetch_execution_history_all_pipelines(maestro_base_url, token)
