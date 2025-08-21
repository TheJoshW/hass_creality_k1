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


async def test_fan_services(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the fan services."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_refresh",
        return_value=True,
    ):
        await setup_integration(
            hass,
            mock_config_entry,
            data={"fan_speed_1": 0, "fan_speed_2": 0, "fan_speed_3": 0},
        )
        coordinator = hass.data["creality_k1"][mock_config_entry.entry_id]
        coordinator.websocket.send_message = AsyncMock()

        # Turn on the fan
        await hass.services.async_call(
            "fan",
            "turn_on",
            {"entity_id": "fan.mock_title_model_fan", "percentage": 50},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S128"}}
        )

        # Turn off the fan
        await hass.services.async_call(
            "fan",
            "turn_off",
            {"entity_id": "fan.mock_title_model_fan"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S0"}}
        )

        # Set speed
        await hass.services.async_call(
            "fan",
            "set_percentage",
            {"entity_id": "fan.mock_title_model_fan", "percentage": 75},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S191"}}
        )


from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_fans_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the fans when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all fan entities
        fans = hass.states.async_all("fan")
        assert len(fans) > 0

        # Assert that all fans are unavailable
        for fan in fans:
            assert fan.state == "unavailable"
