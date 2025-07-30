import requests
import json
import logging
import datetime
from . import data_assets
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def get_all_metabase_dashboards(maestro_base_url: str, token: str):
    """Retrieve all dashboards from Maestro with a valid dashboard_id.

    Args:
        maestro_base_url (str): Base URL of the Maestro instance
            (e.g., 'https://maestro.example.com/api').
        token (str): Authentication token for API access.

    Returns:
        List[Dict]: List of dashboards with valid dashboard_id.
    Example:
        >>> assets = get_all_metabase_dashboards(
        ...     maestro_base_url="https://maestro.example.com/api",
        ...     token="bearer_token_123")
        >>> logger.info(f"Retrieved {len(assets)} Metabase Dashboards")

    """
    data_assets = data_assets.fetch_paginated_catalog_assets(
        maestro_base_url=maestro_base_url,
        token=token,
        additional_params={"data_asset_type": "dashboard"},
    )
    return [
        data_asset
        for data_asset in data_assets
        if data_asset.get("dashboard_id") is not None
    ]
