"""
Implementation of the /scrape endpoint for the Web Extract Data package.
"""
from typing import Dict, Any
import requests


def scrape(api_key: str, 
           url: str, 
           fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured data from any webpage with a single call.
    
    Args:
        api_key (str): Your InstantAPI.ai key
        url (str): The URL of the webpage to scrape
        fields (Dict[str, Any]): The fields to extract in JSON format
    
    Returns:
        Dict[str, Any]: The scraped data
    
    Raises:
        Exception: If the API returns an error
    """
    # Prepare the endpoint and headers
    endpoint = "https://instantapi.ai/api/scrape/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Prepare the payload
    payload = {
        "url": url,
        "fields": fields,
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
