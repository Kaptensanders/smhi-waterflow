"""Client for interacting with the SMHI API."""
import logging
import asyncio
from typing import Dict, Any, Optional

from custom_components.waterflow.const import (
    USER_AGENT,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)

class SMHIClient:
    """Client for fetching data from the SMHI API with retry logic."""
    BASE_URL = "https://vattenwebb.smhi.se/hydronu/"

    def __init__(self, session, logger=None, timeout: Optional[int] = None):
        """Initialize the SMHI client.
        
        Args:
            session: The aiohttp ClientSession to use for requests
            logger: Optional logger instance
            timeout: Optional request timeout in seconds
        """
        self.session = session
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.headers = {
            "User-Agent": USER_AGENT
        }

    async def fetch_data(self, subid: str, x: str, y: str) -> Dict[str, Any]:
        """Fetch data from SMHI API with retry logic.
        
        Args:
            subid: The subid parameter for the SMHI API
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Dictionary containing point_data, chart_data, and production_time
            
        Raises:
            ValueError: If required data is missing
            Exception: If API requests fail after retries
        """
        # Step 1: Fetch point data with retries
        point_url = f"{self.BASE_URL}data/point?x={x}&y={y}"
        point_data = await self._fetch_with_retry(point_url, "point data")

        production_time = point_data.get("productionTime")
        if not production_time:
            raise ValueError("Missing productionTime in point data")

        # Step 2: Fetch chart data with retries
        chart_url = f"{self.BASE_URL}data/chart?subid={subid}&productionTime={production_time}"
        chart_data = await self._fetch_with_retry(chart_url, "chart data")

        return {
            "point_data": point_data,
            "chart_data": chart_data,
            "production_time": production_time
        }
        
    async def _fetch_with_retry(self, url: str, description: str) -> Dict[str, Any]:
        """Fetch data from URL with retry logic.
        
        Args:
            url: The URL to fetch
            description: Description for logging
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.logger.debug(f"Fetching {description}: {url} (attempt {attempt}/{MAX_RETRIES})")
                
                # Use the session provided via dependency injection
                # Set timeout via the timeout parameter if the session supports it
                kwargs = {}
                if hasattr(self.session, "timeout") and self.timeout:
                    kwargs["timeout"] = self.timeout
                
                async with self.session.get(url, headers=self.headers, **kwargs) as resp:
                    resp.raise_for_status()
                    return await resp.json()
                    
            except Exception as err:
                self.logger.warning(
                    f"Error fetching {description} (attempt {attempt}/{MAX_RETRIES}): {err}"
                )
                if attempt == MAX_RETRIES:
                    self.logger.error(f"Failed to fetch {description} after {MAX_RETRIES} attempts")
                    raise
                await asyncio.sleep(RETRY_DELAY * attempt)  # Exponential backoff