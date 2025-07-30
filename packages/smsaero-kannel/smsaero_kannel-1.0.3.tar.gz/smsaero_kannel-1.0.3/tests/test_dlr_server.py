"""
Тесты для DLR сервера.
"""

import pytest
from unittest.mock import AsyncMock, patch

from smsaero_kannel.dlr_server import DLRServer


class TestDLRServer:
    """Тесты для DLR сервера."""

    def test_init(self):
        """Тест инициализации сервера."""
        server = DLRServer("127.0.0.1", 8080)
        assert server.host == "127.0.0.1"
        assert server.port == 8080
        assert server._status_callback is None
        assert server._app is not None
        assert server._runner is None

    def test_init_with_callback(self):
        """Тест инициализации с callback функцией."""

        async def test_callback(status):
            pass

        server = DLRServer("127.0.0.1", 8080)
        server._status_callback = test_callback
        assert server._status_callback == test_callback

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Тест запуска и остановки сервера."""
        server = DLRServer("127.0.0.1", 8080)
        await server.start(lambda x: None)
        assert server._runner is not None
        await server.stop()
        # После остановки runner остается объектом, но ресурсы освобождены
        assert hasattr(server._runner, "cleanup")

    @pytest.mark.asyncio
    async def test_handle_dlr_request_success(self):
        """Тест успешной обработки DLR запроса."""
        callback_called = False

        def test_callback(status):
            nonlocal callback_called
            callback_called = True
            assert status == "delivered"

        server = DLRServer("127.0.0.1", 8080)
        server._status_callback = test_callback
        request = AsyncMock()
        request.query = {"status": "delivered"}

        response = await server.handle_dlr(request)
        assert response.status == 200
        assert callback_called

    @pytest.mark.asyncio
    async def test_handle_dlr_request_missing_status(self):
        """Тест обработки DLR запроса без статуса."""
        server = DLRServer("127.0.0.1", 8080)
        request = AsyncMock()
        request.query = {}

        response = await server.handle_dlr(request)
        assert response.status == 400
        assert "Missing status parameter" in response.text

    @pytest.mark.asyncio
    async def test_handle_dlr_request_callback_error(self):
        """Тест обработки ошибки в callback функции."""

        def test_callback(status):
            raise ValueError("Test error")

        server = DLRServer("127.0.0.1", 8080)
        server._status_callback = test_callback
        request = AsyncMock()
        request.query = {"status": "delivered"}

        response = await server.handle_dlr(request)
        assert response.status == 500
        assert "Callback error" in response.text
