"""Tests for the Creality K1 climate platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_climates(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the climates."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all climate entities
        climates = hass.states.async_all("climate")
        assert len(climates) > 0

        # Assert that the state of each climate matches the snapshot
        for climate in climates:
            assert climate == snapshot(name=f"{climate.entity_id}")
