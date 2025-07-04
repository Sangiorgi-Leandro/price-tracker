import re
from decimal import Decimal, InvalidOperation
from bs4 import BeautifulSoup
import logging

# Import custom HTTP client for making requests
from http_client import HTTPClient

# Import project configuration, including target URLs for scrapers
from config import SCRAPERS

# Get a logger instance for this specific module.
# The logger name will typically be 'scraper.amazon', which helps in tracing logs.
logger = logging.getLogger(__name__)


async def scrape_amazon(client: HTTPClient) -> dict | None:
    """
    Asynchronously scrapes product information (title, price, URL) from an Amazon product page.

    This function attempts to extract the product's title and its current selling price
    using various robust parsing techniques tailored for Amazon's dynamic HTML structure.
    It logs its progress and any issues encountered during the scraping process.

    Args:
        client (HTTPClient): An instance of the custom HTTPClient for making web requests.
                             This client handles retries, timeouts, and user agent rotation.

    Returns:
        dict | None: A dictionary containing 'site', 'title', 'price', and 'url'
                     if the scraping is successful. Returns None if the initial
                     HTML content cannot be fetched.
                     Errors during price parsing are logged, but the function still
                     returns available data with 'Price parse error' or 'Price not found'.
    """
    cfg = SCRAPERS[
        "amazon"
    ]  # Get Amazon-specific configuration from SCRAPERS dictionary
    url = cfg["url"]  # Extract the target URL for Amazon

    # Log the start of the scraping process for this specific URL
    logger.info(f"Scraping Amazon product from: {url}")

    # Fetch the HTML content of the Amazon product page using the HTTP client
    html = await client.fetch(url)
    if not html:
        # If fetching fails (e.g., network error, non-200 status), log a warning and return None
        logger.warning(f"Failed to fetch HTML from {url}. Returning None.")
        return None

    # Parse the HTML content using BeautifulSoup with the 'lxml' parser for efficiency
    soup = BeautifulSoup(html, "lxml")

    # --- Extract Product Title ---
    # Attempt to find the product title using multiple strategies, as Amazon's HTML can vary.
    title = None

    # Strategy 1: Look for the common product title span by its ID
    el = soup.find("span", id="productTitle")
    if el:
        title = el.get_text(
            strip=True
        )  # Extract text and remove leading/trailing whitespace
        logger.debug(f"Found title from span#productTitle: '{title}'")
    else:
        logger.debug("span#productTitle not found, trying alternatives...")

    # Strategy 2: Fallback to a generic H1 heading
    if not title:
        el = soup.find("h1")
        if el:
            title = el.get_text(strip=True)
            logger.debug(f"Found title from h1: '{title}'")

    # Strategy 3: Check the Open Graph (og:title) meta tag, often used for social sharing
    if not title:
        meta = soup.find("meta", property="og:title")
        if meta and meta.get("content"):
            title = meta["content"].strip()
            logger.debug(f"Found title from og:title meta tag: '{title}'")

    # Strategy 4: As a last resort, try parsing the <title> tag content,
    # splitting by common delimiters to get the main product name
    if not title and soup.title:
        raw_head = soup.title.get_text(strip=True)
        # Use regex to split the title tag content, typically at ':', '|', '-'
        title = re.split(r"[:\|\-–]", raw_head)[0].strip()
        logger.debug(f"Found title from title tag fallback: '{title}'")

    # If no title is found after all attempts, set a default message and log a warning
    if not title:
        title = "Title not found"
        logger.warning(
            "Product title could not be extracted by any method on Amazon page."
        )

    # --- Extract Product Price ---
    # Attempt to find and parse the product's price.
    price = "Price not found"

    # Strategy 1: Look for the primary offscreen price element within a 'a-price' span.
    # This is often where Amazon stores the clean, machine-readable price.
    offscreen = soup.select_one("span.a-price > span.a-offscreen")

    # Strategy 2: Fallback to more specific price selectors if the first one fails.
    # These IDs (corePrice_desktop, priceblock_ourprice) are common for main product prices.
    if not offscreen:
        offscreen = soup.select_one(
            "#corePrice_desktop span.a-offscreen, #priceblock_ourprice span.a-offscreen"
        )

    # Strategy 3: Generic a-offscreen as a final attempt, in case the price is in
    # any other offscreen element.
    if not offscreen:
        offscreen = soup.select_one("span.a-offscreen")

    # If an offscreen price element is successfully found
    if offscreen:
        raw_txt = offscreen.get_text(strip=True)  # Get the raw text, e.g., "482,00€"
        logger.debug(f"Raw price text from Amazon a-offscreen: '{raw_txt}'")

        # Clean the raw text: remove all characters except digits, commas, and periods.
        # This gets rid of currency symbols (€, $), spaces, etc.
        cleaned = re.sub(r"[^\d,\.]", "", raw_txt)
        logger.debug(f"Cleaned price text after regex: '{cleaned}'")

        # Normalize the cleaned string for Decimal conversion.
        # This handles common European (1.234,56) and American (1,234.56) number formats.
        if "," in cleaned and "." in cleaned:
            # If both comma and period are present (e.g., "1.234,56"), assume comma is decimal separator
            # and period is thousands separator. Remove periods, then replace comma with period.
            normalized = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            # If only a comma is present (e.g., "123,45"), assume it's the decimal separator.
            # Replace comma with a period.
            normalized = cleaned.replace(",", ".")
        else:
            # If only a period is present (e.g., "123.45") or no separators,
            # assume it's already in a standard format or period is decimal separator.
            normalized = cleaned

        logger.debug(f"Normalized price for Decimal conversion: '{normalized}'")

        try:
            # Convert the normalized string to a Decimal for precise arithmetic.
            dec = Decimal(normalized)
            # Format the Decimal back to a string with 2 decimal places and the Euro symbol.
            price = f"€{dec:.2f}"
            logger.debug(f"Successfully parsed Amazon price: '{price}'")
        except InvalidOperation:
            # If Decimal conversion fails (e.g., due to unexpected characters or format),
            # assign an error message and log a detailed error.
            price = "Price parse error"
            logger.error(
                f"Failed to parse price for Amazon from normalized '{normalized}' (raw: '{raw_txt}')"
            )
    else:
        # If no offscreen price element was found by any selector, log a warning.
        logger.warning("No offscreen price element found for Amazon on the page.")

    # Return a dictionary with the extracted product details.
    return {
        "site": cfg["site"],
        "title": title,
        "price": price,
        "url": url,
    }
