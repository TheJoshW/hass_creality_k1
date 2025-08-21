"""Tests for the Creality K1 integration."""
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def setup_integration(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> ConfigEntry:
    """Set up the Creality K1 integration in Home Assistant."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.creality_k1.coordinator.MyWebSocket", autospec=True
    ) as mock_client:
        client = mock_client.return_value
        client.is_connected = True
        client.disconnect.return_value = True

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    return mock_config_entry
