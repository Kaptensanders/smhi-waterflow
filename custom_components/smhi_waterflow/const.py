"""Constants for the Waterflow integration."""
from datetime import timedelta

# Integration
DOMAIN = "smhi-waterflow"
SCAN_INTERVAL = timedelta(hours=6)

# API Client Settings
USER_AGENT = "Mozilla/5.0 (compatible; SMHIWaterflowIntegration/1.0; +https://github.com/Kaptensanders/smhi-waterflow)"
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
