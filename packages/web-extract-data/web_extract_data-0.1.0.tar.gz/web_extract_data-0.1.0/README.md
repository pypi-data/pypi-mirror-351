# Web Extract Data

A Python package for extracting structured data from websites without writing a single HTML selector.

Web Extract Data provides native functions for each endpoint of the InstantAPI.ai Web Scraping API, making it easy to extract data from websites, find links, navigate through pagination, and scrape Google Search results.

## Installation

```bash
pip install web-extract-data
```

## Quick Start

```python
from web_extract_data import WebExtractClient

# Initialize the client with your InstantAPI.ai key
# Replace %% API_KEY %% with your API key from:
# https://web.instantapi.ai/#pricing-03-254921

client = WebExtractClient("%%API_KEY%%")

# You can modify the URL and data fields to extract in JSON format
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

# Print the extracted data
print(result)
```

## API Reference

### WebExtractClient

The main client class for interacting with the InstantAPI.ai Web Scraping API.

```python
client = WebExtractClient(api_key)
```

- `api_key` (str): Your InstantAPI.ai key.

### Scrape Endpoint

Extract structured data from any webpage.

```python
result = client.scrape(url, fields)
```

- `url` (str): The URL of the webpage to scrape.
- `fields` (dict): The data fields to extract in JSON format.

Example:

```python
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
```

### Links Endpoint

Find all links on a page that match a specific description.

```python
result = client.links(url, description)
```

- `url` (str): The URL of the webpage to scrape.
- `description` (str): Description of the links to extract.

Example:

```python
result = client.links(
    url="https://www.ikea.com/au/en/cat/quilt-cover-sets-10680/?page=3",
    description="individual product urls"
)
```

### Next Page Endpoint

Extract "Next Page" links from a paginated web page.

```python
result = client.next(url)
```

- `url` (str): The URL of the webpage to scrape.

Example:

```python
result = client.next(
    url="https://www.ikea.com/au/en/cat/quilt-cover-sets-10680/"
)
```

### Search Endpoint

Scrape and extract relevant Google search result URLs.

```python
result = client.search(query, google_domain="www.google.com", page=1)
```

- `query` (str): The search query.
- `google_domain` (str, optional): The Google domain to search on. Defaults to "www.google.com".
- `page` (int, optional): The page number to scrape. Defaults to 1.

Example:

```python
result = client.search(
    query="AVID POWER 20V MAX Lithium Ion Cordless Drill Set",
    google_domain="www.google.com",
    page=1
)
```

## Error Handling

The package will raise exceptions if the API returns an error. You can handle these exceptions with a try-except block:

```python
try:
    result = client.scrape(url="https://example.com", fields={"title": "< The title of the page. >"})
    print(result)
except Exception as e:
    print(f"An error occurred: {e}")
```

## Need Help?

Join the [Discord Community](https://discord.gg/pZEJMCTzA3) for real-time help and feedback.

## License

[MIT](LICENSE)
