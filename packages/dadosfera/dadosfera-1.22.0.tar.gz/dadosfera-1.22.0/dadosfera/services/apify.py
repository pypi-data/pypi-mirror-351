import os
import json
from typing import Any, Dict, List


def get_dataset_from_apify(dataset_name: str) -> List[Dict[str, Any]]:
    """Retrieve dataset items from Apify storage using the official client.

    This function connects to Apify's storage service, retrieves or creates a dataset
    by name, and downloads all items from it. The function requires an Apify API key
    to be set in the environment variables.

    Args:
        dataset_name (str): Name of the dataset in Apify storage.
            Case-sensitive name of an existing dataset or name for a new one.
            Example: "my-scraped-data-2024" or "competitor-analysis"

    Returns:
        List[Dict[str, Any]]: List of items from the dataset.
            Each item is a dictionary with structure depending on the dataset content.

    Raises:
        apify_client.exceptions.ApifyApiError: When API calls to Apify fail.
            Common cases:
            - Invalid API key
            - Rate limit exceeded
            - Network issues
            - Invalid dataset name format

        KeyError: When APIFY_API_KEY environment variable is not set.

        json.JSONDecodeError: When the dataset content is not valid JSON.

        UnicodeDecodeError: When the dataset content cannot be decoded as UTF-8.

    Example:
        >>> # Assuming APIFY_API_KEY is set in environment variables
        >>> dataset = get_dataset_from_apify("my-web-scraper-results")
        >>> print(f"Retrieved {len(dataset)} items")
        >>> for item in dataset:
        ...     print(f"Found item: {item['title']}")

    Notes:
        - Requires APIFY_API_KEY environment variable to be set
        - Creates new dataset if name doesn't exist
        - Downloads entire dataset into memory
        - Uses UTF-8 encoding for dataset content
        - Returns empty list if dataset is empty

    Environment Variables:
        APIFY_API_KEY (str): The API key for Apify service.

    See Also:
        - Apify API Documentation:
          https://docs.apify.com/api/v2
        - Apify Client Python:
          https://docs.apify.com/api/client/python/
        - Apify Dataset Documentation:
          https://docs.apify.com/platform/storage/dataset
    """
    from apify_client import ApifyClient

    APIFY_KEY = os.environ["APIFY_API_KEY"]
    apify_client = ApifyClient(APIFY_KEY)
    dataset_metadata = apify_client.datasets().get_or_create(name=dataset_name)
    dataset = apify_client.dataset(dataset_metadata["id"])
    return json.loads(dataset.download_items().decode("utf-8"))
