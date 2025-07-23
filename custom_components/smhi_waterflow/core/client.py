"""Client for interacting with the SMHI API."""
import logging
import asyncio
from typing import Dict, Any, Optional

from custom_components.smhi_waterflow.const import (
    USER_AGENT,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)

class SMHIClient:
    """Client for fetching data from the SMHI API with retry logic."""
    BASE_URL = "https://vattenwebb.smhi.se/hydronu/"

    def __init__(self, session, logger=None, timeout: Optional[int] = None):
        self.session = session
        self.logger = logger or logging.getLogger(__name__)
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.headers = {
            "User-Agent": USER_AGENT
        }

    async def fetch_data(self, subid: str) -> Dict[str, Any]:

        # Fetch point data with retries
        subid_url = f"{self.BASE_URL}data/point?subid={subid}"
        subid_data = await self._fetch_with_retry(subid_url, "point data")
        production_time = subid_data.get("productionTime")
        if not production_time:
            raise ValueError("Missing productionTime in point data")

        return {
            "chart_data": subid_data.get("chartData"),
            "production_time": production_time
        }
        
    async def _fetch_with_retry(self, url: str, description: str) -> Dict[str, Any]:
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