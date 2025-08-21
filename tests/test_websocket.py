"""Tests for the Creality K1 websocket."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.creality_k1.websocket import MyWebSocket


@pytest.fixture
def mock_hass() -> MagicMock:
    """Mock HomeAssistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.async_create_task.side_effect = lambda coro: asyncio.create_task(coro)
    return hass


async def test_websocket_connection(mock_hass):
    """Test the websocket connection logic."""
    ws = MyWebSocket(mock_hass, "ws://test.url", MagicMock())

    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        # Test successful connection
        mock_ws_client = AsyncMock()
        mock_ws_client.recv.side_effect = asyncio.CancelledError  # To break the receive loop
        mock_connect.return_value = mock_ws_client
        await ws.connect()
        assert ws.is_connected
        mock_connect.assert_called_once_with("ws://test.url", ping_interval=None, ping_timeout=None)
        await ws.disconnect()

        # Test connection failure
        ws._is_connected = False # Reset for next test
        mock_connect.side_effect = OSError("Connection refused")
        await ws.connect()
        assert not ws.is_connected


async def test_websocket_message_handling(mock_hass):
    """Test the websocket message handling logic."""
    callback = MagicMock()
    ws = MyWebSocket(mock_hass, "ws://test.url", callback)

    # Test handling of "ok" message
    await ws.handle_message("ok")
    callback.assert_not_called()

    # Test handling of valid JSON message
    await ws.handle_message('{"key": "value"}')
    callback.assert_called_once_with({"key": "value"})

    # Test handling of invalid JSON message
    with patch("custom_components.creality_k1.websocket._LOGGER.warning") as mock_warning:
        await ws.handle_message("invalid json")
        mock_warning.assert_called_once()


async def test_websocket_disconnection(mock_hass):
    """Test the websocket disconnection logic."""
    ws = MyWebSocket(mock_hass, "ws://test.url", MagicMock())
    ws.ws = AsyncMock()
    ws._is_connected = True
    ws.heartbeat_task = asyncio.create_task(asyncio.sleep(1))
    ws.receive_task = asyncio.create_task(asyncio.sleep(1))

    heartbeat_task = ws.heartbeat_task
    receive_task = ws.receive_task

    await ws.disconnect()
    await asyncio.sleep(0)  # Allow cancellation to propagate
    assert not ws.is_connected
    assert ws.ws is None
    assert heartbeat_task.cancelled()
    assert receive_task.cancelled()
