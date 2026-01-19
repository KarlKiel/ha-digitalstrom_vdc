"""Async sensor platform for DigitalSTROM VDC."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


class DigitalstromSensor(SensorEntity):
    """Simple sensor reporting number of configured vDCs on the host."""

    def __init__(self, hub: Any):
        self.hub = hub
        self._attr_name = "DigitalSTROM vDC Count"
        self._attr_unique_id = f"digitalstrom_vdc_count_{hub.port}"
        self._state = None

    @property
    def native_value(self):
        return self._state

    async def async_update(self) -> None:
        # Read state from hub (async-safe)
        try:
            vdcs = []
            if hasattr(self.hub, "get_all_vdcs"):
                vdcs = await self.hub.hass.async_add_executor_job(self.hub.get_all_vdcs)
            elif getattr(self.hub, "_vdc_host", None) is not None:
                vdcs = await self.hub.hass.async_add_executor_job(self.hub._vdc_host.get_all_vdcs)
            self._state = len(vdcs) if isinstance(vdcs, (list, tuple)) else 0
        except Exception:
            self._state = 0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensor platform from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hub = hass.data[DOMAIN].get(entry.entry_id)
    if hub is None:
        return False

    sensor = DigitalstromSensor(hub)
    async_add_entities([sensor], True)
    return True
