import re
from decimal import (
    Decimal,
    InvalidOperation,
)  # Used for precise monetary calculations and error handling
from bs4 import BeautifulSoup  # HTML parsing library
from http_client import HTTPClient  # Custom HTTP client for requests
from config import SCRAPERS  # Project configuration, including target URLs

# Regex to find common European price formats (e.g., 1.234,56 or 123,45).
# It captures digits, optional thousands separators (periods), and two decimal places (comma-separated).
PRICE_REGEX = re.compile(r"(\d{1,3}(?:\.\d{3})*,\d{2})")


def parse_price(text: str) -> Decimal | None:
    """
    Parses a string to find and normalize a price value.
    It attempts to find all price occurrences in the text, then prioritizes
    the last value found that is less than 1000 (common for single items),
    falling back to the very last valid price if no such value exists.

    Args:
        text (str): The input string potentially containing price information.

    Returns:
        Decimal | None: The normalized price as a Decimal object if found and valid,
                        otherwise None.
    """
    # Clean the input text by replacing non-breaking spaces with standard spaces and stripping whitespace.
    clean_text = text.replace("\u00a0", " ").replace("&nbsp;", " ").strip()

    # Find all occurrences of the defined price pattern in the cleaned text.
    matches = PRICE_REGEX.findall(clean_text)
    if not matches:
        return None  # No price patterns found

    # Attempt to find the most relevant price by iterating from the end.
    # This logic assumes that for a single product, the price displayed will usually be under 1000.
    for raw_price_str in reversed(matches):
        try:
            # Normalize the price string: remove thousands separators (periods) and
            # replace the decimal comma with a period for Decimal conversion.
            val = Decimal(raw_price_str.replace(".", "").replace(",", "."))
            if (
                val < 1000
            ):  # Prioritize values under 1000, common for single item prices.
                return val
        except InvalidOperation:
            # Continue if a matched string can't be converted to a valid Decimal.
            continue

    # Fallback: If no price under 1000 is found, return the very last valid price found.
    # This handles cases where the main product price might be over 1000, or other prices were present.
    if matches:  # Ensure there's at least one match left after the loop
        try:
            return Decimal(matches[-1].replace(".", "").replace(",", "."))
        except InvalidOperation:
            return None  # Still invalid
    return None  # No valid prices found after all attempts


async def scrape_phoneclick(client: HTTPClient) -> dict | None:
    """
    Scrapes product information (title, price, URL) from Phoneclick.it.

    Args:
        client (HTTPClient): An instance of the custom HTTPClient for making requests.

    Returns:
        dict | None: A dictionary containing 'site', 'title', 'price', and 'url'
                     if successful, otherwise None.
    """
    # Get Phoneclick-specific configuration, including the target URL.
    cfg = SCRAPERS["phoneclick"]

    # Fetch the HTML content of the Phoneclick product page.
    html = await client.fetch(cfg["url"])

    # Parse the HTML content with BeautifulSoup.
    soup = BeautifulSoup(html, "lxml")

    # --- Extract Product Title ---
    # Attempt to find the main title using a specific class, then fall back to any <h1> tag.
    title_el = soup.find("h1", class_="caratteretitolo") or soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else "Title not found"

    # --- Extract Product Price ---
    # Initialize price to None.
    price: Decimal | None = None

    # 1) Primary attempt: Look for price within an <ins> tag (often used for sale/discounted prices).
    ins_tag = soup.find("ins")
    if ins_tag:
        # Parse the text content of the <ins> tag for a price.
        extracted_price = parse_price(ins_tag.get_text())
        if extracted_price is not None:
            price = extracted_price

    # 2) Fallback: If no price found in <ins>, search for any text containing '€'.
    if price is None:
        candidate_prices = []
        # Iterate through all visible text strings on the page.
        for text_string in soup.stripped_strings:
            if "€" in text_string:  # Check if the euro symbol is present.
                # Attempt to parse a price from this text string.
                val = parse_price(text_string)
                if val is not None:
                    candidate_prices.append(val)

        if candidate_prices:
            # If multiple candidates found, select the last valid price.
            # This heuristic often works for pages with multiple price mentions.
            price = candidate_prices[-1]

    # Format the final extracted price for output.
    price_str = f"€{price:.2f}" if price is not None else "Price not found"

    # Return a dictionary with the scraped data.
    return {
        "site": cfg["site"],
        "title": title,
        "price": price_str,
        "url": cfg["url"],
    }
