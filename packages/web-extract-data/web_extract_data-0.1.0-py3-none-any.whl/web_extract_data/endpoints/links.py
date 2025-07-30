"""
Implementation of the /links endpoint for the Web Extract Data package.
"""
from typing import Dict, Any
import requests


def links(api_key: str, 
          url: str, 
          description: str) -> Dict[str, Any]:
    """
    Find all links on a page that match a specific description.
    
    Args:
        api_key (str): Your InstantAPI.ai key
        url (str): The URL of the webpage to scrape
        description (str): Description of the links to extract
    
    Returns:
        Dict[str, Any]: The extracted links
    
    Raises:
        Exception: If the API returns an error
    """
    # Prepare the endpoint and headers
    endpoint = "https://instantapi.ai/api/links/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Prepare the payload
    payload = {
        "url": url,
        "description": description,
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
