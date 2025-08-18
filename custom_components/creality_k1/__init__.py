"""Creality K1 Integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import CrealityK1DataUpdateCoordinator  # DataUpdateCoordinator class from coordinator.py

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Creality K1 from a config entry."""

    # Store coordinator instance per entry for platform access
    hass.data.setdefault(DOMAIN, {})
    coordinator = CrealityK1DataUpdateCoordinator(hass, config_entry)
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    # Trigger initial connection
    await coordinator.async_config_entry_first_refresh()

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS) # Use PLATFORMS

    if unload_ok:
        # Get the specific websocket instance and close it.
        if config_entry.entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][config_entry.entry_id]
            await coordinator.websocket.disconnect()

            # Delete all data for this entry
            hass.data[DOMAIN].pop(config_entry.entry_id)

        # Remove whole domain if no more entries 
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Reload config entry."""
    return await hass.config_entries.async_reload(config_entry.entry_id)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Running migration of config entry")
    return True