import os
import uuid
import requests
import json
from typing import Any, Dict, Literal, Optional
from datetime import datetime
import time
import re
import unidecode
import logging
import anybase32
from types import SimpleNamespace
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

BASE_PIPELINE_URL = "https://oz8v2zid1e.execute-api.us-east-1.amazonaws.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

METHOD = Literal["GET", "POST", "DELETE", "PUT", "PATH"]


def word_special_character_remover(word: str) -> str:
    """Remove special characters from a word and replace them with underscores.

    Args:
        word (str): The word to sanitize.

    Returns:
        str: The sanitized word.
    """
    return re.sub("[^0-9a-zA-Z_]+", "_", unidecode.unidecode(word))


def get_zbase_32_pipeline_id(pipeline_id: str) -> str:
    """Convert the given pipeline ID to zbase32 format.

    Args:
        pipeline_id (str): The pipeline ID to convert.

    Returns:
        str: The zbase32 formatted pipeline ID.
    """
    original_pipeline_id = pipeline_id.replace("_", "-")
    uuid_bytes = uuid.UUID(original_pipeline_id).bytes
    return anybase32.encode(bytearray(uuid_bytes), anybase32.ZBASE32).decode("utf-8")


def create_table_name(data_asset_name: str, pipeline_id: str) -> str:
    """Create a table name based on a data asset name and pipeline ID.

    Args:
        data_asset_name (str): The name of the data asset.
        pipeline_id (str): The ID of the pipeline.

    Returns:
        str: The generated table name.
    """
    data_asset_name = data_asset_name.replace(".", "__")
    data_asset_sanitized = word_special_character_remover(data_asset_name)
    base32_pipeline_id = get_zbase_32_pipeline_id(pipeline_id=pipeline_id)
    return f"tb__{base32_pipeline_id[:6]}__{data_asset_sanitized}"


def create_simplenamespace() -> SimpleNamespace:
    """Create a SimpleNamespace object containing AWS credentials.

    Returns:
        SimpleNamespace: A SimpleNamespace object with AWS credentials.
    """
    credentials = boto3.Session().get_credentials()
    token = "" if credentials.token is None else credentials.token
    return SimpleNamespace(
        access_key=credentials.access_key,
        secret_key=credentials.secret_key,
        token=token,
    )


def sign_aws_iam_v4(
    method: METHOD,
    url: str,
    data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    service: str = "execute-api",
) -> Dict[str, str]:
    """Sign an AWS request using the IAM V4 signature method.

    Args:
        method (METHOD): The HTTP method.
        url (str): The request URL.
        data (Optional[Dict[str, str]]): The request data payload.
        headers (Optional[Dict[str, str]]): The request headers.
        service (str, optional): The AWS service name. Default is "execute-api".

    Returns:
        Dict[str, str]: The signed headers for the request.
    """
    creds = create_simplenamespace()
    request = AWSRequest(method=method, url=url, data=data)
    SigV4Auth(
        creds, service, os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    ).add_auth(request)
    if headers is None:
        headers = {}
    headers.update(request.headers)
    return headers


def get_headers(
    method: METHOD,
    url: str,
    data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Get the appropriate headers for a request, based on the environment.

    Args:
        method (METHOD): The HTTP method.
        url (str): The request URL.
        data (Optional[Dict[str, str]]): The request data payload.
        headers (Optional[Dict[str, str]]): The request headers.

    Returns:
        Dict[str, str]: A dictionary of headers for the request.
    """
    if os.environ.get("ENV") in ["local", "test"]:
        return {"Content-Type": "application/json"}
    return sign_aws_iam_v4(method=method, url=url, headers=headers, data=data)


def pipeline_last_status(platform_api_base_url: str, pipeline_id: str) -> str:
    """Get the last status of a pipeline.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        pipeline_id (str): The ID of the pipeline.

    Returns:
        str: The last status of the pipeline.
    """
    url = f"{platform_api_base_url}/pipeline/{pipeline_id}/pipeline_run"
    headers = get_headers("GET", url=url, headers={})
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    if len(r.json()) > 0:
        pipeline_runs = r.json()
        return max(
            pipeline_runs, key=lambda x: datetime.fromisoformat(x["created_at"])
        )["last_status"]
    return "NO_PIPELINE_RUNS"


def poll_for_terminal_state(
    platform_api_base_url: str, pipeline_id: str, poll_interval=10
) -> None:
    """Polls the pipeline_last_status until it reaches a terminal state (FAILED, SUCCESS).

    Args:
        platform_api_base_url (str): Base URL of the platform API.
        pipeline_id (str): The ID of the pipeline to check.
        poll_interval (int, optional): Time in seconds between each poll. Default is 10 seconds.

    Returns:
        str: The terminal state of the pipeline.
    """
    terminal_states = ["FAILED", "SUCCESS"]
    while True:
        current_status = pipeline_last_status(platform_api_base_url, pipeline_id)
        logger.info(
            f"The current status of the last run of pipeline_id {pipeline_id} is {current_status}"
        )
        if current_status in terminal_states:
            return current_status
        time.sleep(poll_interval)


def delete_pipeline(
    platform_api_base_url: str, pipeline_id: str, customer_name: str
) -> None:
    """Delete a pipeline.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        pipeline_id (str): The ID of the pipeline to delete.
        customer_name (str): The name of the customer.
    """
    url = f"{platform_api_base_url}/pipeline/{pipeline_id}"
    headers = get_headers("DELETE", url=url, headers={"customer_name": customer_name})
    r = requests.delete(url, headers=headers)
    r.raise_for_status()
    logger.info(f"Successfully deleted pipeline: {pipeline_id}")


def update_jdbc_dataset_asset(
    platform_api_base_url: str, job_id: str, payload: Dict[str, Any]
) -> None:
    """Update a JDBC dataset asset.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        job_id (str): The ID of the job to update.
        payload (Dict[str, Any]): The data payload for the update.
    """
    url = f"{platform_api_base_url}/data_assets/jdbc/{job_id}"
    headers = get_headers("PATCH", url=url, headers=None, data=json.dumps(payload))
    logger.info(f"Making request to {url}")
    r = requests.patch(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        logger.info(
            f"The request has returned an status code different than 200. More details: {r.text}"
        )
        r.raise_for_status()
    logger.info(f"Successfully patched the job_id: {job_id}")


def jdbc_reset_job_state(platform_api_base_url: str, job_id: str) -> None:
    """Reset the state of a JDBC job.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        job_id (str): The ID of the job to reset.
    """
    logger.info(f"Reseting the job state of the job {job_id}")
    update_jdbc_dataset_asset(
        platform_api_base_url=platform_api_base_url,
        job_id=job_id,
        payload={"incremental_column_value": None},
    )


def jdbc_update_from_incremental_to_full_table(
    platform_api_base_url: str, job_id: str
) -> None:
    """Update a JDBC job from incremental to full table loading.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        job_id (str): The ID of the job to update.
    """
    logger.info(
        f"Updating the job_type of the job_id {job_id}. From incremental to full load."
    )
    update_jdbc_dataset_asset(
        platform_api_base_url=platform_api_base_url,
        job_id=job_id,
        payload={
            "incremental_column_name": None,
            "incremental_column_value": None,
            "load_type": "full_table",
        },
    )


def jdbc_update_from_full_table_to_incremental(
    platform_api_base_url: str, incremental_column_name: str, job_id: str
) -> None:
    """Update a JDBC job from full table to incremental loading.

    Args:
        platform_api_base_url (str): The base URL of the platform API.
        incremental_column_name (str): The name of the incremental column.
        job_id (str): The ID of the job to update.
    """
    logger.info(
        f"Updating the job_type of the job_id {job_id}. From Full Load to Incremental."
    )
    update_jdbc_dataset_asset(
        platform_api_base_url=platform_api_base_url,
        job_id=job_id,
        payload={
            "incremental_column_name": incremental_column_name,
            "load_type": "incremental",
        },
    )
    logger.info("Success")


def update_job_memory(
    platform_api_base_url: str, job_id: str, memory_allocation_mb: int
) -> None:
    """
    Update the memory allocation for a specific job in the platform.

    Args:
        platform_api_base_url (str): The base URL for the platform API.
        job_id (str): The unique identifier for the job to be updated.
        memory_allocation_mb (int): The amount of memory (in megabytes) to allocate for the job.

    Returns:
        None

    Raises:
        HTTPError: If the request to the platform API returns a status code other than 200.
    """
    url = f"{platform_api_base_url}/jobs/{job_id}/memory"

    payload = {"amount": memory_allocation_mb}
    headers = get_headers("PUT", url=url, headers=None, data=json.dumps(payload))
    logger.info(f"Making request to {url}")
    r = requests.put(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        logger.info(
            f"The request has returned an status code different than 200. More details: {r.text}"
        )
        r.raise_for_status()
    logger.info(f"Successfully updated the memory for job_id: {job_id}")


def update_pipeline_memory(
    platform_api_base_url: str, pipeline_id: str, memory_allocation_mb: int
) -> None:
    """
    Update the memory allocation for a specific pipeline in the platform.

    Args:
        platform_api_base_url (str): The base URL for the platform API.
        pipeline_id (str): The unique identifier for the pipeline to be updated.
        memory_allocation_mb (int): The amount of memory (in megabytes) to allocate for the pipeline.

    Returns:
        None

    Raises:
        HTTPError: If the request to the platform API returns a status code other than 200.
    """
    url = f"{platform_api_base_url}/pipeline/{pipeline_id}/memory"

    payload = {"amount": memory_allocation_mb}
    headers = get_headers("PUT", url=url, headers=None, data=json.dumps(payload))
    logger.info(f"Making request to {url}")
    r = requests.put(url=url, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        logger.info(
            f"The request has returned an status code different than 200. More details: {r.text}"
        )
        r.raise_for_status()
    logger.info(f"Successfully updated the memory for pipeline_id: {pipeline_id}")
