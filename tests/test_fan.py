"""Tests for the Creality K1 fan platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_fans(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the fans."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all fan entities
        fans = hass.states.async_all("fan")
        assert len(fans) > 0

        # Assert that the state of each fan matches the snapshot
        for fan in fans:
            assert fan == snapshot(name=f"{fan.entity_id}")
