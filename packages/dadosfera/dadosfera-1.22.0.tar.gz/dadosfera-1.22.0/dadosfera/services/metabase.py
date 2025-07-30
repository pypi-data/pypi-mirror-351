import logging
from typing import Dict
import httpx

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def metabase_token(metabase_base_url, metabase_username, metabase_password) -> str:
    """
    Authenticates with the Metabase API and returns a session token.

    Args:
        metabase_base_url (str): Base URL of the Metabase instance
        metabase_username (str): Username for Metabase authentication
        metabase_password (str): Password for Metabase authentication

    Returns:
        str: Session token for Metabase API authentication

    Example:
        token = await metabase_token("https://metabase.example.com", "admin", "password123")
        print(token)

    Note:
        - Requires valid Metabase credentials
        - The token expires after a certain period and may need to be refreshed
        - Raises an exception if authentication fails
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{metabase_base_url}/api/session",
            json={"username": metabase_username, "password": metabase_password},
        )
        response.raise_for_status()
        data = response.json()
        return data["id"]


async def create_automagically_dashboard(
    metabase_base_url: str,
    metabase_token: str,
    table_id: int
) -> Dict:
    """
    Creates an automatically generated dashboard based on a specific table in Metabase.

    Args:
        metabase_base_url (str): Base URL of the Metabase instance
        metabase_token (str): Authentication token for API access
        table_id (int): ID of the table to create a dashboard for

    Returns:
        Dict: Response from the API containing the created dashboard information

    Example:
        dashboard = await create_automagically_dashboard(
            "https://metabase.example.com", 
            "token123", 
            42
        )
        print(f"Created dashboard with ID: {dashboard['id']}")

    Note:
        - Uses Metabase's automagic dashboard feature which analyzes table data
        - The dashboard is created but not automatically saved to a collection
        - The quality of the generated dashboard depends on the table structure
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{metabase_base_url}/api/automagic-dashboards/table/{table_id}",
            headers={"X-Metabase-Session": metabase_token},
        )
        response.raise_for_status()
        payload = response.json()

        response = await client.post(
            f"{metabase_base_url}/api/dashboard/save",
            json=payload,
            headers={"X-Metabase-Session": metabase_token},
        )
        response.raise_for_status()
        return response.json()
    

async def get_dashboard_cards(dashboard_id: int,
                             metabase_base_url: str,
                             metabase_token: str) -> list:
    """
    Retrieves all cards (visualizations) from a specific Metabase dashboard.
    
    Args:
        dashboard_id (int): ID of the dashboard to retrieve cards from
        metabase_base_url (str): Base URL of the Metabase instance
        metabase_token (str): Authentication token for API access
    
    Returns:
        list: List of dashboard cards with their IDs and metadata
    
    Example:
        cards = await get_dashboard_cards(123, "https://metabase.example.com", "token123")
        for card in cards:
            print(f"Card ID: {card['card_id']}, Title: {card.get('card', {}).get('name')}")
    
    Note:
        - Returns all cards regardless of their type (questions, text cards, etc.)
        - Each card contains metadata about its position, size, and configuration
        - The response includes the full dashboard structure, but this function extracts only the cards
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{metabase_base_url}/api/dashboard/{dashboard_id}",
            headers={"X-Metabase-Session": metabase_token},
        )
        response.raise_for_status()
        data = response.json()
        
        return data["dashcards"]


async def get_cards_query_results(cards: list,
                                 metabase_base_url: str,
                                 metabase_token: str) -> list:
    """
    Retrieves query results for all cards in a dashboard.
    
    Args:
        cards (list): List of dashboard cards
        metabase_base_url (str): Base URL of the Metabase instance
        metabase_token (str): Authentication token for API access
    
    Returns:
        list: Query results for each card in the dashboard
    
    Example:
        cards = await get_dashboard_cards(123, "https://metabase.example.com", "token123")
        results = await get_cards_query_results(cards, "https://metabase.example.com", "token123")
        for result in results:
            print(f"Data rows: {len(result.get('data', {}).get('rows', []))}")
    
    Note:
        - Skips cards that don't have a card_id (such as text cards)
        - Executes each card's query to get fresh results
        - The results contain both the data and metadata about columns
        - For large dashboards, this function may take significant time to complete
    """
    cards_metadata = []
    async with httpx.AsyncClient() as client:
        for card in cards:
            if card["card_id"] is not None:
                response = await client.post(
                    f"{metabase_base_url}/api/card/{card['card_id']}/query",
                    headers={"X-Metabase-Session": metabase_token},
                )
                response.raise_for_status()
                cards_metadata.append(response.json())
    
    return cards_metadata


async def describe_dashboard(dashboard_id: int, 
                            metabase_base_url: str, 
                            metabase_token: str) -> list:
    """
    Provides a comprehensive description of a dashboard by retrieving all its cards and their query results.
    
    Args:
        dashboard_id (int): ID of the dashboard to describe
        metabase_base_url (str): Base URL of the Metabase instance
        metabase_token (str): Authentication token for API access
    
    Returns:
        list: Metadata and query results for all cards in the dashboard
    
    Example:
        dashboard_data = await describe_dashboard(
            123, 
            "https://metabase.example.com", 
            "token123"
        )
        print(f"Dashboard contains {len(dashboard_data)} cards with data")
    
    Note:
        - This is a convenience function that combines get_dashboard_cards and get_cards_query_results
        - For large dashboards with many visualizations, this function may be time-intensive
        - The returned data structure contains the full query results for each card
        - Can be used for dashboard export, analysis, or migration purposes
    """
    cards = await get_dashboard_cards(dashboard_id, metabase_base_url, metabase_token)
    cards_metadata = await get_cards_query_results(cards, metabase_base_url, metabase_token)
    
    return cards_metadata