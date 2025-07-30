import httpx
import requests
import json
from typing import List, Optional, Dict, Literal
import logging
from time import sleep
import base64
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_vector_dataset(
    base_url: str,
    filepaths: List[str],
    ocr_method: Literal["premium", "common"] = "common",
):
    """Creates a vector dataset from uploaded files and monitors until completion.

    This function uploads multiple files to a dataset creation service and
    waits until the dataset is fully processed. It periodically checks the
    dataset status until it reaches a terminal state.

    Args:
        base_url: Base URL of the service.
        filepaths: List of file paths to be uploaded.
        ocr_method: OCR quality setting. "premium" for high-quality OCR (slower)
            or "common" for standard OCR (faster). Defaults to "common".

    Returns:
        tuple: A tuple containing:
            - dict: Dataset details including status information
            - str: Dataset ID of the created dataset

    Raises:
        HTTPError: If any API request fails with a non-200 status code.
    """

    files = [
        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
        for file_path in filepaths
    ]
    data = {"ocr_method": ocr_method}

    authorization = create_basic_auth(username="admin", password=extract_id(base_url))

    # Header
    headers = {
        "Authorization": authorization,
    }

    response = requests.post(
        url=f"{base_url}/upload", headers=headers, files=files, data=data
    )

    if response.status_code != 200:
        logger.error(response.content)
        response.raise_for_status()

    dataset_id = response.json()["dataset_id"]

    terminal_states = ["success", "failed"]
    sleep_interval = 60 if ocr_method == "premium" else 5
    logger.info("Checking if dataset is ready")
    state = None
    while True:
        logger.info(f"Dataset {dataset_id} not ready yet, waiting some seconds.")
        response = requests.get(f"{base_url}/dataset/{dataset_id}")
        if response.status_code != 200:
            response.raise_for_status()

        if response.status_code == 200:
            state = response.json()["status"]

            if state in terminal_states:
                logger.info(f"Response: {response.json()}")
                return response.json(), dataset_id

        logger.info(f"Response not ready yet, awaiting {sleep_interval}")
        sleep(sleep_interval)


def ask_question_to_dataset(
    base_url: str,
    dataset_id: str,
    question: str,
    metadata_filter: Optional[Dict] = None,
    distance_metric: Literal["cos", "L2", "L1", "max", "dot"] = "cos",
    maximize_marginal_relevance: bool = True,
    fetch_k: int = 10,
    k: int = 3,
):
    """Queries a vector dataset with a natural language question.

    This function sends a question to a previously created dataset and
    waits for the answer to be generated. It periodically checks the
    question status until it reaches a terminal state.

    Args:
        base_url: Base URL of the service.
        dataset_id: Unique identifier of the dataset to query.
        question: The natural language question text.
        metadata_filter: Optional dictionary to filter documents by metadata.
            Defaults to None.
        distance_metric: Vector similarity metric to use. Options include:
            "cos" (cosine), "L2" (Euclidean), "L1", "max", or "dot" product.
            Defaults to "cos".
        maximize_marginal_relevance: Whether to use MMR to diversify results.
            Defaults to True.
        fetch_k: Number of neighbors to fetch initially. Defaults to 10.
        k: Final number of results to return. Defaults to 3.

    Returns:
        dict: Response containing the answer and related information.

    Raises:
        HTTPError: If any API request fails with a non-200 status code.
    """
    authorization = create_basic_auth(username="admin", password=extract_id(base_url))

    # Header
    headers = {
        "Authorization": authorization,
    }

    response = requests.post(
        url=f"{base_url}/dataset/{dataset_id}/question",
        headers={"Content-Type": "application/json", **headers},
        data=json.dumps(
            {
                "question": question,
                "metadata_filter": metadata_filter,
                "distance_metric": distance_metric,
                "maximize_marginal_relevance": maximize_marginal_relevance,
                "fetch_k": fetch_k,
                "k": k,
            }
        ),
    )

    if response.status_code != 200:
        logger.error(response.content)
        response.raise_for_status()

    question_id = response.json()["question_id"]

    terminal_states = ["success", "failed"]
    logger.info("Checking if question is ready")
    state = None
    while True:
        logger.info(f"Question {question_id} not ready yet, waiting some seconds.")
        response = requests.get(
            f"{base_url}/dataset/{dataset_id}/question/{question_id}",
            headers={"Content-Type": "application/json", **headers},
        )
        if response.status_code != 200:
            response.raise_for_status()

        state = response.json()["status"]

        if state in terminal_states:
            logger.info(f"Response: {response.json()}")
            return response.json()

        sleep(5)


def create_basic_auth(username: str, password: str) -> str:
    """Creates a Basic Authentication header value.

    Generates a Base64-encoded Basic Authentication header from
    username and password credentials.

    Args:
        username: The username for authentication.
        password: The password for authentication.

    Returns:
        str: A properly formatted Basic Authentication header value in the format:
            "Basic <base64-encoded-credentials>".
    """
    # Concatena o username e password no formato `username:password`
    credentials = f"{username}:{password}"

    # Codifica as credenciais em Base64
    credentials_bytes = credentials.encode("utf-8")
    base64_bytes = base64.b64encode(credentials_bytes)

    # Converte de volta para string
    base64_credentials = base64_bytes.decode("utf-8")

    # Retorna a string completa de 'Basic <Base64_encoded_credentials>'
    return f"Basic {base64_credentials}"


def extract_id(url):
    """Extracts a UUID from the end of a URL.

    Parses a URL string to extract a UUID that appears at the end.

    Args:
        url: URL string potentially containing a UUID at the end.

    Returns:
        str or None: The extracted UUID if found, None otherwise.
    """
    # Expressão regular para capturar o ID (um padrão de UUID)
    match = re.search(r"[0-9a-fA-F\-]{36}$", url)
    if match:
        return match.group(0)
    else:
        return None


def ask_question_to_dataset_using_ai(
    base_url: str,
    dataset_id: str,
    question: str,
    metadata_filter: Optional[Dict] = None,
    distance_metric: Literal["cos", "L2", "L1", "max", "dot"] = "cos",
    maximize_marginal_relevance: bool = True,
    fetch_k: int = 10,
    k: int = 3,
):
    """Queries a vector dataset with AI-enhanced question answering.

    Similar to ask_question_to_dataset but specifically uses a LLM to
    process and answer the question based on retrieved documents.

    Args:
        base_url: Base URL of the service.
        dataset_id: Unique identifier of the dataset to query.
        question: The natural language question text.
        metadata_filter: Optional dictionary to filter documents by metadata.
            Defaults to None.
        distance_metric: Vector similarity metric to use. Options include:
            "cos" (cosine), "L2" (Euclidean), "L1", "max", or "dot" product.
            Defaults to "cos".
        maximize_marginal_relevance: Whether to use MMR to diversify results.
            Defaults to True.
        fetch_k: Number of neighbors to fetch initially. Defaults to 10.
        k: Final number of results to return. Defaults to 3.

    Returns:
        dict: Response containing the AI-generated answer and related information.

    Raises:
        HTTPError: If any API request fails with a non-200 status code.
    """
    authorization = create_basic_auth(username="admin", password=extract_id(base_url))
    headers = {
        "Authorization": authorization,
    }

    response = requests.post(
        url=f"{base_url}/dataset/{dataset_id}/ai_question",
        headers={"Content-Type": "application/json", **headers},
        data=json.dumps(
            {
                "question": question,
                "metadata_filter": metadata_filter,
                "distance_metric": distance_metric,
                "maximize_marginal_relevance": maximize_marginal_relevance,
                "fetch_k": fetch_k,
                "k": k,
            }
        ),
    )

    if response.status_code != 200:
        logger.error(response.content)
        response.raise_for_status()

    question_id = response.json()["question_id"]

    terminal_states = ["success", "failed"]
    logger.info("Checking if question is ready")
    state = None
    while True:
        logger.info(f"Question {question_id} not ready yet, waiting some seconds.")
        response = requests.get(
            f"{base_url}/dataset/{dataset_id}/ai_question/{question_id}",
            headers={"Content-Type": "application/json", **headers},
        )
        if response.status_code != 200:
            response.raise_for_status()

        state = response.json()["status"]

        if state in terminal_states:
            logger.info(f"Response: {response.json()}")
            return response.json()
        sleep(5)


def list_datasets(base_url: str, name: str = None, limit: int = 10, offset: int = 0):
    """Lists available datasets with optional filtering and pagination.

    Retrieves a list of datasets from the service with support for
    filtering by name and pagination controls.

    Args:
        base_url: Base URL of the service.
        name: Optional filter to search datasets by name. Defaults to None.
        limit: Maximum number of results to return. Defaults to 10.
        offset: Number of results to skip (for pagination). Defaults to 0.

    Returns:
        dict: JSON response containing the list of datasets and pagination metadata.

    Raises:
        HTTPError: If the API request fails with a non-200 status code.
    """
    authorization = create_basic_auth(username="admin", password=extract_id(base_url))
    headers = {
        "Authorization": authorization,
    }

    response = requests.get(
        url=f"{base_url}/datasets",
        headers={"Content-Type": "application/json", **headers},
        params={"name": name, "limit": limit, "offset": offset},
    )

    if response.status_code != 200:
        logger.error(response.content)
        response.raise_for_status()

    return response.json()


async def update_dataset(base_url: str, dataset_id: str, filepaths: List[str]):
    """Asynchronously updates a dataset with new files.

    Uploads additional files to an existing dataset using an asynchronous HTTP request.

    Args:
        base_url: Base URL of the service.
        dataset_id: Unique identifier of the dataset to update.
        filepaths: List of file paths to be uploaded and added to the dataset.

    Returns:
        dict or None: JSON response if successful, None if an error occurs.
    """
    authorization = create_basic_auth(username="admin", password=extract_id(base_url))
    headers = {
        "Authorization": authorization,
    }
    files = [
        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
        for file_path in filepaths
    ]
    url = f"{base_url}/dataset/{dataset_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url, headers=headers, files=files, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            raise Exception


async def get_dataset(base_url: str, dataset_id: str):
    """Asynchronously retrieves dataset information.

    Gets detailed information about a specific dataset using an asynchronous HTTP request.

    Args:
        base_url: Base URL of the service.
        dataset_id: Unique identifier of the dataset to retrieve.

    Returns:
        dict or None: Dataset details if successful, None if an error occurs.
    """
    authorization = create_basic_auth(username="admin", password=extract_id(base_url))
    headers = {
        "Authorization": authorization,
    }
    url = f"{base_url}/dataset/{dataset_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            raise Exception
            
