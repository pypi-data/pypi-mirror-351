"""
Implementation of the /search endpoint for the Web Extract Data package.
"""
from typing import Dict, Any
import requests


def search(api_key: str, 
           query: str, 
           google_domain: str = "www.google.com", 
           page: int = 1) -> Dict[str, Any]:
    """
    Scrape and extract relevant Google search result URLs.
    
    Args:
        api_key (str): Your InstantAPI.ai key
        query (str): The search query
        google_domain (str, optional): The Google domain to search on. Defaults to "www.google.com".
        page (int, optional): The page number to scrape. Defaults to 1.
    
    Returns:
        Dict[str, Any]: The search results
    
    Raises:
        Exception: If the API returns an error
    """
    # Prepare the endpoint and headers
    endpoint = "https://instantapi.ai/api/search/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Prepare the payload
    payload = {
        "query": query,
        "google_domain": google_domain,
        "page": page,
    }

    # Make the request
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response_json = response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")

    # Determine if there was an error
    have_error = response_json.get("error") is True and response_json.get("reason") is not None

    # Check if the request was successful
    if have_error:
        raise Exception(f"Error: {response_json.get('reason')}")
    elif response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.text}")
    
    # Return the response
    return response_json
