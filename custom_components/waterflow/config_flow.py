import logging
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class WaterflowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Waterflow."""

    VERSION = 1

    async def async_step_import(self, user_input=None):
        """Handle import from configuration.yaml."""
        if user_input is not None:
            return await self._handle_config(user_input)
        return self.async_abort(reason="missing_configuration")

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return await self._handle_config(user_input)

        return self.async_show_form(
            step_id="user", 
            data_schema=self._get_schema(),
            errors=errors
        )
    
    async def _handle_config(self, user_input):
        """Handle the configuration data and create or update an entry."""
        if "name" not in user_input:
            return self.async_abort(reason="missing_name")
            
        # Use name as the unique ID
        unique_id = user_input["name"]
        
        # Check if an entry with this unique ID already exists
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        
        # Create the config entry with the name as the title
        title = f"Waterflow {unique_id}"
        return self.async_create_entry(title=title, data=user_input)

    def _get_schema(self):
        """Get the schema for the config flow."""
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol

        return vol.Schema({
            vol.Required("name"): str,
            vol.Required("x"): vol.Coerce(float),
            vol.Required("y"): vol.Coerce(float),
            vol.Required("subid"): cv.positive_int,
        })
