"""Tests for the Creality K1 button platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_buttons(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the buttons."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all button entities
        buttons = hass.states.async_all("button")
        assert len(buttons) > 0

        # Assert that the state of each button matches the snapshot
        for button in buttons:
            assert button == snapshot(name=f"{button.entity_id}")
