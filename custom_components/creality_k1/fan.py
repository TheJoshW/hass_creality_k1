# fan.py (Version 3 - med GCODE M106)
"""Platform for Creality K1 fans that support percentage control via GCODE."""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, FAN_CONFIG, FAN_NAME_AUXILIARY_FAN, FAN_NAME_CASE_FAN, FAN_NAME_MODEL_FAN, DEVICE_MANUFACTURER, DEVICE_MODEL
from .coordinator import CrealityK1DataUpdateCoordinator
from .helpers import get_hw_sw_versions

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    ) -> None:
    """Set up the Creality K1 fans from a config entry."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id] # Get correct coordinator when having multiple printers
    fans = []
    icons = {
        FAN_NAME_MODEL_FAN: "mdi:fan-speed-1",
        FAN_NAME_CASE_FAN: "mdi:fan-speed-2",
        FAN_NAME_AUXILIARY_FAN: "mdi:fan-speed-3",
    }
    for name, (percent_key, toggle_key, p_index) in FAN_CONFIG.items():
        fans.append(
            K1Fan(
                coordinator,
                percent_key,
                toggle_key,
                p_index, # Pass GCODE P-index
                config_entry,
                name,
                icons.get(name, "mdi:fan"),
            )
        )
    async_add_entities(fans)


class K1Fan(CoordinatorEntity, FanEntity):
    """Representation of a Creality K1 Fan using M106 GCODE."""

    _attr_has_entity_name = True
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        percentage_key: str,
        toggle_key: str,
        p_index: int, # GCODE P-Index (P0, P1, P2)
        config_entry: ConfigEntry,
        name: str,
        icon: str,
        ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._percentage_key = percentage_key
        self._toggle_key = toggle_key
        self._p_index = p_index # Store GCODE P-index
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{config_entry.entry_id}_fan_{toggle_key.lower()}"
        self._config_entry = config_entry
        _LOGGER.debug(
            f"Initializing Fan: {self.name} ({self.unique_id}) "
            f"using keys Pct='{self._percentage_key}', Toggle='{self._toggle_key}', GcodeP={self._p_index}"
            )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        (hw_version, sw_version) = get_hw_sw_versions(self.coordinator.data)
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self.coordinator.data.get('hostname', self._config_entry.title),
            manufacturer=DEVICE_MANUFACTURER,
            model=self.coordinator.data.get('model', DEVICE_MODEL),
            hw_version=hw_version,
            sw_version=sw_version,
            via_device=(DOMAIN, self._config_entry.entry_id)
        )

    @property
    def available(self) -> bool:
        return self.coordinator.websocket.is_connected and super().available

    @property
    def is_on(self) -> bool | None:
        """Return true if the fan is on (based on toggle key)."""
        # State reading remains the same as v2
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            toggle_value = self.coordinator.data.get(self._toggle_key)
            if toggle_value is None:
                return None
            try:
                return int(toggle_value) == 1
            except (ValueError, TypeError):
                return None
        return None

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        # State reading remains the same as v2
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            current_is_on = self.is_on
            if current_is_on is False:
                return 0
            elif current_is_on is None:
                return None

            value = self.coordinator.data.get(self._percentage_key)
            if value is None:
                return None
            try:
                return max(0, min(100, int(value)))
            except (ValueError, TypeError):
                return None
        return None

    async def _send_m106_command(self, speed_0_255: int) -> None:
        """Helper function to send M106 S<speed> P<index> GCODE command."""
        safe_speed = max(0, min(255, speed_0_255))
        gcode = f"M106 P{self._p_index} S{safe_speed}"
        command = {"method": "set", "params": {"gcodeCmd": gcode}}
        _LOGGER.debug(f"Fan {self.name}: Sending command: {command}")
        try:
            await self.coordinator.websocket.send_message(command)
            # Update HA state optimistically
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Fan {self.name}: Failed to send M106 command: {e}")

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan using M106 S<0-255>."""
        _LOGGER.debug(f"Fan {self.name}: Setting percentage to {percentage}")
        if percentage < 0 or percentage > 100:
            _LOGGER.warning(f"Fan {self.name}: Invalid percentage {percentage} requested")
            return

        # Convert 0-100 percentage to 0-255 value
        speed_0_255 = round(percentage / 100 * 255)
        await self._send_m106_command(speed_0_255)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
        ) -> None:
        """Turn on the fan using M106."""
        _LOGGER.debug(f"Fan {self.name}: Turn on requested. Percentage={percentage}")
        if percentage is None:
            # Default to 100% -> S255
            target_speed_0_255 = 255
            _LOGGER.debug(f"Fan {self.name}: No percentage specified, defaulting to 100% (S255)")
        else:
            target_percentage = max(1, min(100, percentage)) # Ensure > 0 if turning on
            target_speed_0_255 = round(target_percentage / 100 * 255)

        await self._send_m106_command(target_speed_0_255)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off using M106 S0."""
        # Alternatively, could send {"method": "set", "params": {self._toggle_key: 0}}
        # But using M106 S0 is consistent with speed control method.
        _LOGGER.debug(f"Fan {self.name}: Turn off requested (M106 S0).")
        await self._send_m106_command(0)