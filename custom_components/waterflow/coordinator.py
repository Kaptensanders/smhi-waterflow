import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .core.client import SMHIClient
from .core.processor import SMHIProcessor
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import COORDINATOR_NAME, SCAN_INTERVAL


_LOGGER = logging.getLogger(__name__)

class WaterflowCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=COORDINATOR_NAME,
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass
        self.entry = entry

    async def _async_update_data(self):

        session = async_get_clientsession(self.hass)
        client = SMHIClient(session, _LOGGER)
        data = await client.fetch_data(
            self.entry.data["subid"],
            self.entry.data["x"],
            self.entry.data["y"]
        )

        processor = SMHIProcessor()
        processed = await self.hass.async_add_executor_job(
            processor.process_data, data["chart_data"]
        )
        processed.update({
            "mq": data["chart_data"].get("mq"),
            "mlq": data["chart_data"].get("mlq"),
            "mhq": data["chart_data"].get("mhq")
        })
        return processed
