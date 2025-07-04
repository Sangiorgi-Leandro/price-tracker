#!/usr/bin/env python3

import asyncio
import random
import json
import csv
import logging
from datetime import datetime

# Import project configurations
from config import (
    HEADERS,
    TIMEOUT,
    DATA_DIR,
    JSON_FILE,
    CSV_FILE,
    RATE_LIMIT,
)
# Import custom modules
from logger import setup_logging
from http_client import HTTPClient
# Import specific scraper functions
from scraper.amazon import scrape_amazon
from scraper.phoneclick import scrape_phoneclick
from scraper.teknozone import scrape_teknozone

# Get a logger instance for this module
logger = logging.getLogger(__name__)

async def main():
    """
    Main asynchronous function to orchestrate the price tracking process.
    It sets up logging, initializes the HTTP client, runs scrapers in parallel,
    and saves the collected data to JSON and CSV files.
    """
    setup_logging()  # Configure the logging system
    logger.info("🚀 Starting price-tracker")

    # Ensure the data directory exists. If it doesn't, create it.
    DATA_DIR.mkdir(exist_ok=True)

    # Initialize the HTTP client. RETRIES are handled internally by HTTPClient.
    client = HTTPClient(headers=HEADERS, timeout=TIMEOUT)

    try:
        # Prepare scraper tasks with random delays to avoid being flagged.
        # This list holds references to the scraper functions.
        scrapers_functions = (scrape_amazon, scrape_phoneclick, scrape_teknozone)
        tasks = []
        for fn in scrapers_functions:
            # Introduce a random delay before creating each task to mimic human-like behavior
            await asyncio.sleep(random.uniform(*RATE_LIMIT))
            tasks.append(fn(client)) # Append the coroutine (function call) to the tasks list

        # Execute scraper tasks concurrently.
        # return_exceptions=True ensures that the program doesn't stop if one scraper fails,
        # allowing us to handle individual failures gracefully.
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process the results: filter out exceptions and collect valid data.
        results = []
        for resp in responses:
            if isinstance(resp, Exception):
                # Log any errors encountered by individual scrapers
                logger.error(f"🛑 Scraper error: {resp}")
            elif resp:
                # If the response is valid (not an exception and not None/empty)
                results.append(resp)

    finally:
        # Ensure the HTTP client session is always closed, even if errors occur.
        await client.close()

    # --- Data Saving ---

    # Save a snapshot of the current scraping results to a JSON file.
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(
            # Include a timestamp for when the data was last updated
            {"last_updated": datetime.now().isoformat(), "prices": results},
            f,
            ensure_ascii=False, # Ensure non-ASCII characters (like product names) are preserved
            indent=2,           # Format JSON with 2-space indentation for readability
        )
    logger.info(f"💾 Saved JSON to {JSON_FILE}")

    # Append the collected data to a CSV file for historical tracking.
    is_new_csv = not CSV_FILE.exists() # Check if the CSV file already exists
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        # Define the CSV headers (fieldnames) for DictWriter
        writer = csv.DictWriter(
            f, fieldnames=["timestamp", "site", "title", "price", "url"]
        )
        if is_new_csv:
            writer.writeheader() # Write headers only if the file is newly created

        # Add a timestamp to each record before writing to CSV
        current_timestamp = datetime.now().isoformat()
        for item in results:
            writer.writerow({"timestamp": current_timestamp, **item}) # Unpack item dictionary
    logger.info(f"📊 Appended {len(results)} records to {CSV_FILE}")

    # --- Console Output ---

    # Print the collected price tracking results to the console.
    print("\n📋 PRICE TRACKING RESULTS")
    print("=" * 60) # Separator line
    if not results:
        print("❌ No data collected.")
    for item in results:
        print(f"🏪 Site:     {item['site']}")
        print(f"📱 Product:  {item['title']}")
        print(f"💰 Price:    {item['price']}")
        print(f"🔗 URL:      {item['url']}")
        print("-" * 40) # Item separator

    logger.info("✅ Tracking completed")


# Entry point for the script
if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())