import requests
import json
from typing import List, Optional, Dict, Literal
import logging
from time import sleep
import base64
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_vector_dataset(base_url: str, filepaths: List[str],ocr_method: Literal['premium','common']='common'):
    """
    Uploads multiple files to a dataset creation service and monitors until the dataset is ready.

    Args:
    - base_url (str): The base URL of the service.
    - filepaths (List[str]): A list of file paths to be uploaded.
    - ocr_method (Literal['premium','common'])

    Returns:
    - dict: A dictionary containing the dataset details. Typically this would include a dataset_id and the status of the creation.

    Raises:
    - HTTPError: If any of the HTTP requests return a non-200 status code.
    """

    files = [
        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
        for file_path in filepaths
    ]
    data = {'ocr_method': ocr_method}

    authorization = create_basic_auth(username = 'admin', password = extract_id(base_url))

    # Header
    headers = {
        'Authorization': authorization,
    }

    response = requests.post(
        url=f"{base_url}/upload",
        headers = headers,
        files=files,
        data=data
    )

    if response.status_code != 200:
        logger.error(response.content)
        response.raise_for_status()

    dataset_id = response.json()["dataset_id"]

    terminal_states = ["success", "failed"]
    sleep_interval = 60 if ocr_method == 'premium' else 5
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

        logger.info(f'Response not ready yet, awaiting {sleep_interval}')
        sleep(sleep_interval)


def ask_question_to_dataset(
        base_url: str,
        dataset_id: str,
        question: str,
        metadata_filter: Optional[Dict] = None,
        distance_metric: Literal["cos","L2","L1","max","dot"] = "cos",
        maximize_marginal_relevance: bool = True,
        fetch_k: int = 10,
        k: int = 3
    ):
    """
    Asks a question to a previously created dataset and monitors until an answer is ready.

    Args:
    - base_url (str): The base URL of the service.
    - dataset_id (str): The unique identifier of the dataset.
    - question (str): The question string.

    Returns:
    - dict: A dictionary containing the answer details. Typically this would include a question_id and the status of the question.

    Raises:
    - HTTPError: If any of the HTTP requests return a non-200 status code.
    """
    authorization = create_basic_auth(username = 'admin', password = extract_id(base_url))

    # Header
    headers = {
        'Authorization': authorization,
    }

    response = requests.post(
        url=f"{base_url}/dataset/{dataset_id}/question",
        headers={"Content-Type": "application/json", **headers},
        data=json.dumps({
            "question": question,
            "metadata_filter": metadata_filter,
            "distance_metric": distance_metric,
            "maximize_marginal_relevance": maximize_marginal_relevance,
            "fetch_k": fetch_k,
            "k": k
        })
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
            headers={"Content-Type": "application/json", **headers}
            )
        if response.status_code != 200:
            response.raise_for_status()

        state = response.json()["status"]

        if state in terminal_states:
            logger.info(f"Response: {response.json()}")
            return response.json()

        sleep(5)

def create_basic_auth(username: str, password: str) -> str:
    # Concatena o username e password no formato `username:password`
    credentials = f"{username}:{password}"

    # Codifica as credenciais em Base64
    credentials_bytes = credentials.encode('utf-8')
    base64_bytes = base64.b64encode(credentials_bytes)

    # Converte de volta para string
    base64_credentials = base64_bytes.decode('utf-8')

    # Retorna a string completa de 'Basic <Base64_encoded_credentials>'
    return f"Basic {base64_credentials}"

def extract_id(url):
    # Expressão regular para capturar o ID (um padrão de UUID)
    match = re.search(r'[0-9a-fA-F\-]{36}$', url)
    if match:
        return match.group(0)
    else:
        return None

def ask_question_to_dataset_using_ai(
        base_url: str,
        dataset_id: str,
        question: str,
        metadata_filter: Optional[Dict] = None,
        distance_metric: Literal["cos","L2","L1","max","dot"] = "cos",
        maximize_marginal_relevance: bool = True,
        fetch_k: int = 10,
        k: int = 3
    ):
    """
    Asks a question for Gemini to a previously created dataset and monitors until an answer is ready.

    Args:
    - base_url (str): The base URL of the service.
    - dataset_id (str): The unique identifier of the dataset.
    - question (str): The question string.

    Returns:
    - dict: A dictionary containing the answer details. Typically this would include a question_id and the status of the question.

    Raises:
    - HTTPError: If any of the HTTP requests return a non-200 status code.
    """
    authorization = create_basic_auth(username = 'admin', password = extract_id(base_url))

    # Header
    headers = {
        'Authorization': authorization,
    }

    response = requests.post(
        url=f"{base_url}/dataset/{dataset_id}/ai_question",
        headers={"Content-Type": "application/json", **headers},
        data=json.dumps({
            "question": question,
            "metadata_filter": metadata_filter,
            "distance_metric": distance_metric,
            "maximize_marginal_relevance": maximize_marginal_relevance,
            "fetch_k": fetch_k,
            "k": k
        })
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
            headers={"Content-Type": "application/json", **headers}
            )
        if response.status_code != 200:
            response.raise_for_status()

        state = response.json()["status"]

        if state in terminal_states:
            logger.info(f"Response: {response.json()}")
            return response.json()

        sleep(5)
