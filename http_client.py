import asyncio
import aiohttp
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Import project configurations, specifically the number of retries
from config import RETRIES

# Get a logger instance for this module, ensuring consistent logging throughout the application.
logger = logging.getLogger(__name__)


class HTTPClient:
    """
    A robust asynchronous HTTP client for making web requests.
    It utilizes aiohttp for efficient concurrent requests and tenacity for automatic retries
    on common network errors.
    """

    def __init__(self, headers: dict, timeout: int):
        """
        Initializes the HTTPClient with a shared aiohttp ClientSession.

        Args:
            headers (dict): Default HTTP headers to be sent with each request.
            timeout (int): Total timeout in seconds for each request.
        """
        self._session = aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)
        )

    @retry(
        # Stop retrying after a maximum number of attempts, defined in config.RETRIES.
        stop=stop_after_attempt(RETRIES),
        # Wait exponentially between retries (1s, 2s, 4s, etc.), up to a max of 10 seconds.
        # This helps to avoid overwhelming the server and respects rate limits.
        wait=wait_exponential(multiplier=1, min=1, max=10),
        # Only retry if specific exceptions occur, indicating a network or timeout issue.
        # This prevents retrying on valid HTTP errors (e.g., 404, 500) that aren't temporary.
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    )
    async def fetch(self, url: str) -> str:
        """
        Fetches the content of a given URL. Includes automatic retries.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The text content of the response.

        Raises:
            aiohttp.ClientError: If the HTTP request fails or returns a non-2xx status code
                                 after all retries are exhausted.
            asyncio.TimeoutError: If the request times out after all retries.
        """
        async with self._session.get(url) as resp:
            # Raise an exception for bad HTTP status codes (4xx or 5xx).
            resp.raise_for_status()
            logger.info(f"Fetched {url} [status={resp.status}]")
            return await resp.text()

    async def close(self):
        """
        Closes the aiohttp client session.
        It's crucial to call this method when the client is no longer needed
        to properly release resources.
        """
        if (
            not self._session.closed
        ):  # Check if session is already closed to prevent errors
            await self._session.close()
