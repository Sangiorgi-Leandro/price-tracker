import re
from decimal import Decimal  # For accurate handling of monetary values
from bs4 import BeautifulSoup  # HTML parsing library
from http_client import HTTPClient  # Custom asynchronous HTTP client
from config import SCRAPERS  # Project configuration, including target URLs


async def scrape_teknozone(client: HTTPClient) -> dict | None:
    """
    Scrapes product information (title, price, URL) from Teknozone.it.

    This scraper specifically looks for prices within <strong> or <span> tags
    that contain the Euro symbol, then extracts the first valid price found.

    Args:
        client (HTTPClient): An instance of the custom HTTPClient for making requests.

    Returns:
        dict | None: A dictionary containing 'site', 'title', 'price', and 'url'
                     if successful. 'price' will be "Price not found" if extraction fails.
    """
    # Get Teknozone-specific configuration, including the target URL.
    cfg = SCRAPERS["teknozone"]

    # Fetch the HTML content of the Teknozone product page.
    html = await client.fetch(cfg["url"])

    # Parse the HTML content with BeautifulSoup.
    soup = BeautifulSoup(html, "lxml")

    # --- Extract Product Title ---
    # Attempt to find the main title using the "product-title" class,
    # then fall back to any <h1> tag if the specific class is not found.
    title_el = soup.find("h1", class_="product-title") or soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else "Title not found"

    # --- Extract Product Price ---
    # Find all <strong> or <span> tags that contain the Euro symbol (€).
    # This is a common pattern for displaying prices on e-commerce sites.
    texts_with_euro = [
        el.get_text(strip=True)
        for el in soup.find_all(["strong", "span"], string=re.compile(r"€"))
    ]

    # Iterate through the extracted texts to find the first valid price.
    for text_string in texts_with_euro:
        # Use regex to find a price pattern: Euro symbol, optional spaces, then digits
        # with either a comma or period as a decimal separator, followed by two decimals.
        # The price value itself is captured in group 1.
        price_match = re.search(r"€\s*(\d+[.,]\d{2})", text_string)
        if price_match:
            # If a match is found, extract the raw price string (e.g., "1.234,56").
            raw_price_value = price_match.group(1)
            # Convert to Decimal: replace comma with period for Python's Decimal type.
            # Then format it back to a string with '€' and two decimal places.
            formatted_price = f"€{Decimal(raw_price_value.replace(',', '.')):.2f}"

            # As soon as the first valid price is found, return the result.
            return {
                "site": cfg["site"],
                "title": title,
                "price": formatted_price,
                "url": cfg["url"],
            }

    # --- Fallback if Price Not Found ---
    # If no price could be extracted after checking all candidates, return with a "Price not found" status.
    return {
        "site": cfg["site"],
        "title": title,
        "price": "Price not found",
        "url": cfg["url"],
    }
