"""Tests for the Creality K1 switch platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_switches(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the switches."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all switch entities
        switches = hass.states.async_all("switch")
        assert len(switches) > 0

        # Assert that the state of each switch matches the snapshot
        for switch in switches:
            assert switch == snapshot(name=f"{switch.entity_id}")
