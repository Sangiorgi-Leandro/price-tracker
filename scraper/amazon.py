import re
from decimal import Decimal, InvalidOperation
from bs4 import BeautifulSoup
from http_client import HTTPClient  # Custom HTTP client for making requests
from config import SCRAPERS  # Project configuration, including target URLs


async def scrape_amazon(client: HTTPClient) -> dict | None:
    """
    Scrapes product information (title, price, URL) from Amazon.

    Args:
        client (HTTPClient): An instance of the custom HTTPClient for making requests.

    Returns:
        dict | None: A dictionary containing 'site', 'title', 'price', and 'url'
                     if successful, otherwise None (errors bubble up via return_exceptions in main).
    """
    cfg = SCRAPERS["amazon"]
    html = await client.fetch(cfg["url"])
    soup = BeautifulSoup(html, "lxml")

    # --- Extract Product Title ---
    title = None

    # 1. span#productTitle (standard product name)
    el = soup.find("span", id="productTitle")
    if el:
        title = el.get_text(strip=True)

    # 2. Generic <h1>
    if not title:
        el = soup.find("h1")
        if el:
            title = el.get_text(strip=True)

    # 3. Meta og:title (social sharing tag)
    if not title:
        meta = soup.find("meta", property="og:title")
        if meta and meta.get("content"):
            title = meta["content"].strip()

    # 4. <title> tag fallback (split on common delimiters)
    if not title and soup.title:
        raw_head = soup.title.get_text(strip=True)
        title = re.split(r"[:\|\-–]", raw_head)[0].strip()

    if not title:
        title = "Title not found"

    # --- Extract Product Price ---
    price = "Price not found"

    # 1. Try the offscreen element inside a-price
    offscreen = soup.select_one("span.a-price > span.a-offscreen")
    # 2. Fallback to any a-offscreen
    if not offscreen:
        offscreen = soup.select_one("span.a-offscreen")

    if offscreen:
        # Raw text might contain "€" and other chars: keep only digits, dots and commas
        raw_txt = offscreen.get_text(strip=True)
        cleaned = re.sub(r"[^\d,\.]", "", raw_txt)

        # Normalize thousands + decimals: "1.234,56" -> "1234.56"
        normalized = cleaned.replace(".", "").replace(",", ".")

        # Parse with Decimal
        try:
            dec = Decimal(normalized)
            price = f"€{dec:.2f}"
        except InvalidOperation:
            price = "Price parse error"

    return {
        "site": cfg["site"],
        "title": title,
        "price": price,
        "url": cfg["url"],
    }
