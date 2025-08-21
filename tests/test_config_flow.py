"""Test the Creality K1 config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries, setup
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.creality_k1.config_flow import CannotConnect
from custom_components.creality_k1.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        return_value=None,
    ) as mock_validate_connection:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Creality K1"
    assert result2["data"] == {
        CONF_IP_ADDRESS: "1.2.3.4",
    }
    assert len(mock_validate_connection.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
