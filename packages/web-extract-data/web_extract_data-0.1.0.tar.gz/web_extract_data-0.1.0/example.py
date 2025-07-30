"""
Example script demonstrating how to use the web-extract-data package.
"""
import json
from web_extract_data import WebExtractClient

# Initialize the client with your InstantAPI.ai key
# Replace %% API_KEY %% with your API key from:
# https://web.instantapi.ai/#pricing-03-254921

client = WebExtractClient("%%API_KEY%%")


def example_scrape():
    """Example of using the scrape endpoint."""
    print("\n--- SCRAPE ENDPOINT EXAMPLE ---")
    
    # Extract monitor details from Amazon
    result = client.scrape(
        url="https://www.amazon.com.au/MSI-PRO-MP341CQW-UltraWide-Compatible/dp/B09Y19TRQ2",
        fields={
            "monitor_name": "< The product name of the monitor. >",
            "brand": "< The brand or manufacturer name. >",
            "display_size_in_inches": "< Numeric only. >",
            "resolution": "< Example format: 1920x1080. >",
            "panel_type": "< Type of panel. >",
            "refresh_rate_hz": "< Numeric only. >",
            "aspect_ratio": "< Example format: 16:9. >",
            "ports": "< A comma-delimited list of available ports (e.g., HDMI, DisplayPort, etc.). >",
            "features": "< Key selling points or capabilities, comma-delimited (e.g., LED, Full HD, etc.). >",
            "price": "< Numeric price (integer or float). >",
            "price_currency": "< Price currency (3 character alphabetic ISO 4217). >",
            "review_count": "< Total number of customer reviews, numeric only. >",
            "average_rating": "< Float or numeric star rating (e.g., 4.3). >",
            "review_summary": "< A 50 words or less summary of all the written customer feedback. >"
        }
    )
    
    print(f"Scrape Result:\n{json.dumps(result.get('scrape'), indent=2)}")


def example_links():
    """Example of using the links endpoint."""
    print("\n--- LINKS ENDPOINT EXAMPLE ---")
    
    # Extract product links from IKEA
    result = client.links(
        url="https://www.ikea.com/au/en/cat/quilt-cover-sets-10680/?page=1",
        description="individual product urls"
    )
    
    print(f"Links Result:\n{json.dumps(result.get('links'), indent=2)}")


def example_next():
    """Example of using the next endpoint."""
    print("\n--- NEXT ENDPOINT EXAMPLE ---")
    
    # Extract next page links from IKEA
    result = client.next(
        url="https://www.ikea.com/au/en/cat/quilt-cover-sets-10680/"
    )
    
    print(f"Next Page Result:\n{json.dumps(result.get('next'), indent=2)}")


def example_search():
    """Example of using the search endpoint."""
    print("\n--- SEARCH ENDPOINT EXAMPLE ---")
    
    # Search for a product on Google
    result = client.search(
        query="AVID POWER 20V MAX Lithium Ion Cordless Drill Set",
        google_domain="www.google.com",
        page=1
    )
    
    print(f"Search Result:\n{json.dumps(result.get('search'), indent=2)}")


if __name__ == "__main__":
    print("Web Extract Data - Usage Examples")
    print("=================================")
    print("Replace %% API_KEY %% with your API key before running.")
    print("Get your API key from: https://web.instantapi.ai/#pricing-03-254921")
    
    # Comment out examples you don't want to run
    example_scrape()
    example_links()
    example_next()
    example_search()
