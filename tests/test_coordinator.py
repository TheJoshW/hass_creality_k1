"""Tests for the Creality K1 data update coordinator."""
from unittest.mock import AsyncMock, patch, PropertyMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.creality_k1.coordinator import CrealityK1DataUpdateCoordinator


async def test_coordinator_connection(hass: HomeAssistant, mock_config_entry):
    """Test the coordinator's connection logic."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)

    with patch.object(
        coordinator.websocket, "connect", AsyncMock()
    ) as mock_connect, patch.object(
        type(coordinator.websocket), "is_connected", new_callable=PropertyMock
    ) as mock_is_connected:
        # Test successful connection
        mock_is_connected.return_value = True
        await coordinator._async_update_data()
        mock_connect.assert_not_called()

        # Test connection failure
        mock_is_connected.return_value = False
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        mock_connect.assert_called_once()


async def test_coordinator_data_processing(hass: HomeAssistant, mock_config_entry):
    """Test the coordinator's data processing logic."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)
    test_data = {"test_key": "test_value"}

    with patch.object(coordinator, "async_set_updated_data") as mock_set_updated_data:
        coordinator.process_raw_data(test_data)
        mock_set_updated_data.assert_called_once_with(test_data)
        assert coordinator.latest_data == test_data
