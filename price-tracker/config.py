import os
import random
from pathlib import Path
from typing import Tuple

# --- Directory and File Paths ---
# Base directory for storing scraped data.
# Defaults to 'data' in the current working directory, but can be overridden by SCRAPER_DATA_DIR environment variable.
DATA_DIR = Path(os.getenv("SCRAPER_DATA_DIR", "data"))
# Path for the JSON file that stores the latest scraped prices.
# Defaults to 'latest_prices.json' inside DATA_DIR.
JSON_FILE = DATA_DIR / os.getenv("SCRAPER_JSON_FILE", "latest_prices.json")
# Path for the CSV file that stores a historical record of prices.
# Defaults to 'price_history.csv' inside DATA_DIR.
CSV_FILE = DATA_DIR / os.getenv("SCRAPER_CSV_FILE", "price_history.csv")

# --- HTTP and Scraping Parameters ---
# Default timeout for HTTP requests in seconds.
# Can be overridden by SCRAPER_TIMEOUT environment variable.
TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "15"))  # seconds
# Number of retries for failed HTTP requests.
# Can be overridden by SCRAPER_RETRIES environment variable.
RETRIES = int(os.getenv("SCRAPER_RETRIES", "3"))  # attempts
# RATE_LIMIT: A tuple defining the minimum and maximum random pause (in seconds)
# between consecutive requests. This helps to mimic human behavior and avoid rate limiting.
# Can be overridden by SCRAPER_RATE_LIMIT environment variable (e.g., "1,3").
RATE_LIMIT: Tuple[float, float] = tuple(
    float(x) for x in os.getenv("SCRAPER_RATE_LIMIT", "1,3").split(",")
)

# --- Rotating User-Agents (helps prevent fingerprinting/blocking) ---
# A list of common and up-to-date User-Agent strings.
# The scraper will pick one randomly for each request (unless overridden by an env var).
USER_AGENTS = [
    # Chrome 126 on Windows desktop
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    # Firefox 127 on MacOS
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) "
        "Gecko/20100101 Firefox/127.0"
    ),
    # Safari 17.5 on MacOS
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.5 Safari/605.1.15"
    ),
    # Chrome mobile on Android
    (
        "Mozilla/5.0 (Linux; Android 12; Pixel 5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Mobile Safari/537.36"
    ),
]

def get_random_user_agent() -> str:
    """
    Retrieves a random User-Agent string from the predefined list.
    If the 'SCRAPER_USER_AGENT' environment variable is set, it will
    override the random selection and use that specific User-Agent.
    """
    return os.getenv("SCRAPER_USER_AGENT") or random.choice(USER_AGENTS)

# --- Standard HTTP Headers for requests ---
# These headers help to make the requests look like they are coming from a real browser.
HEADERS = {
    "User-Agent": get_random_user_agent(), # Dynamically set User-Agent
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    # Preferred language for content negotiation.
    # Can be overridden by SCRAPER_ACCEPT_LANGUAGE environment variable.
    "Accept-Language": os.getenv("SCRAPER_ACCEPT_LANGUAGE", "en-US,en;q=0.9,it;q=0.8"), # Changed default to en-US
    "Accept-Encoding": "gzip, deflate, br", # Specifies accepted content encodings
    "Cache-Control": "max-age=0", # Request no caching
    "DNT": "1", # Do Not Track request
    "Connection": "keep-alive", # Keep the connection alive for multiple requests
    # Security headers often sent by modern browsers:
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Upgrade-Insecure-Requests": "1", # Request upgrade to HTTPS
}

# --- Proxy Configuration (optional) ---
# A list of proxy URLs (e.g., "http://user:pass@host:port").
# Proxies can be provided via the 'SCRAPER_PROXIES' environment variable,
# as a comma-separated string (e.g., "proxy1,proxy2").
PROXIES = [
    p.strip() for p in os.getenv("SCRAPER_PROXIES", "").split(",") if p.strip()
]

# --- Website URLs for Scraping ---
# A dictionary defining the target websites and their default URLs.
# Each URL can be overridden by a specific environment variable
# (e.g., SCRAPER_AMAZON_URL, SCRAPER_PHONECLICK_URL, SCRAPER_TEKNOZONE_URL).
SCRAPERS = {
    "amazon": {
        "site": "amazon.it",
        "url": os.getenv(
            "SCRAPER_AMAZON_URL",
            "https://www.amazon.it/dp/B0C78GHQRJ/"
        ),
    },
    "phoneclick": {
        "site": "phoneclick.it",
        "url": os.getenv(
            "SCRAPER_PHONECLICK_URL",
            "https://www.phoneclick.it/samsung/galaxy-s23/samsung-galaxy-s23-5g-256gb-8gb-ram-dual-sim-black-europa"
        ),
    },
    "teknozone": {
        "site": "teknozone.it",
        "url": os.getenv(
            "SCRAPER_TEKNOZONE_URL",
            "https://www.teknozone.it/smartphone-samsung/galaxy-s23/samsung-galaxy-s23-5g-256gb-8gb-ram-dual-sim-black-europa"
        ),
    },
}

# --- File Permissions (Optional Security Measure) ---
# Attempts to set more restrictive file permissions (read/write only for owner)
# for this configuration file on Unix-like systems (0o600).
# This can help protect sensitive configurations if any were present.
try:
    os.chmod(__file__, 0o600)
except Exception:
    # Ignores errors, e.g., if running on Windows or without sufficient permissions.
    pass