from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        WaterflowSensor(coordinator, entry, "waterflow"),
        WaterflowSensor(coordinator, entry, "precipitation"),
        WaterflowSensor(coordinator, entry, "waterflow_history"),
        WaterflowInfoEntity(coordinator, entry),
    ]
    async_add_entities(entities)


class WaterflowSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} {key.replace('_', ' ').title()}"
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def native_value(self):
        return None

    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": self.coordinator.entry.data["name"],
            "manufacturer": "SMHI",
            "model": "Waterflow Station",
            "configuration_url": "https://vattenwebb.smhi.se/hydronu/",
        }


class WaterflowInfoEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_name = f"{entry.data['name']} Info"
        self._attr_unique_id = f"{entry.entry_id}_info"

    @property
    def native_value(self):
        return None

    @property
    def extra_state_attributes(self):
        return {
            "mq": self.coordinator.data.get("mq"),
            "mlq": self.coordinator.data.get("mlq"),
            "mhq": self.coordinator.data.get("mhq"),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": self.coordinator.entry.data["name"],
            "manufacturer": "SMHI",
            "model": "Waterflow Station",
            "configuration_url": "https://vattenwebb.smhi.se/hydronu/",
        }
