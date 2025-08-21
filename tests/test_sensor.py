"""Tests for the Creality K1 sensor platform."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_sensors(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the sensors."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        entry = await setup_integration(hass, mock_config_entry)

        # Get all sensor entities
        sensors = hass.states.async_all("sensor")
        assert len(sensors) > 0  # Ensure some sensors were created

        # Assert that the state of each sensor matches the snapshot
        for sensor in sensors:
            assert sensor == snapshot(name=f"{sensor.entity_id}")
