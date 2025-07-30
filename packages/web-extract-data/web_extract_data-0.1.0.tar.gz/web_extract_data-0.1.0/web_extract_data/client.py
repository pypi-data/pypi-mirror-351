"""
WebExtractClient - Main client class for the Web Extract Data package.
"""
from typing import Dict, List, Any, Optional, Union

from .endpoints.scrape import scrape
from .endpoints.links import links
from .endpoints.next import next
from .endpoints.search import search


class WebExtractClient:
    """
    Client for extracting structured data from websites using the InstantAPI.ai Web Scraping API.
    
    This client provides native functions for each endpoint of the InstantAPI.ai Web Scraping API,
    making it easy to extract data from websites without writing HTML selectors.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the WebExtractClient with your API key.
        
        Args:
            api_key (str): Your InstantAPI.ai key
            
        Raises:
            Exception: If the API key is empty or still has the default placeholder
        """
        if not api_key or api_key.strip() == "" or "%%API_KEY%%" in api_key:
            raise Exception(
                "Please provide a valid InstantAPI.ai API key. "
                "You can get your API key from: https://web.instantapi.ai/#pricing-03-254921"
            )
        
        self.api_key = api_key
    
    def scrape(self, 
               url: str, 
               fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from any webpage with a single call.
        
        Args:
            url (str): The URL of the webpage to scrape
            fields (Dict[str, Any]): The fields to extract in JSON format
        
        Returns:
            Dict[str, Any]: The scraped data
        """
        return scrape(self.api_key, url, fields)
    
    def links(self, 
              url: str, 
              description: str) -> Dict[str, Any]:
        """
        Find all links on a page that match a specific description.
        
        Args:
            url (str): The URL of the webpage to scrape
            description (str): Description of the links to extract
        
        Returns:
            Dict[str, Any]: The extracted links
        """
        return links(self.api_key, url, description)
    
    def next(self, 
                  url: str) -> Dict[str, Any]:
        """
        Extract "Next Page" links from a paginated web page.
        
        Args:
            url (str): The URL of the webpage to scrape
        
        Returns:
            Dict[str, Any]: The next page links
        """
        return next(self.api_key, url)
    
    def search(self, 
               query: str, 
               google_domain: str = "www.google.com", 
               page: int = 1) -> Dict[str, Any]:
        """
        Scrape and extract relevant Google search result URLs.
        
        Args:
            query (str): The search query
            google_domain (str, optional): The Google domain to search on. Defaults to "www.google.com".
            page (int, optional): The page number to scrape. Defaults to 1.
        
        Returns:
            Dict[str, Any]: The search results
        """
        return search(self.api_key, query, google_domain, page)
