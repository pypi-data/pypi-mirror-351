"""
Тесты для асинхронного клиента Kannel.
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch

from smsaero_kannel import AsyncKannel
from smsaero_kannel.errors import KannelConnectionError


class TestAsyncKannel:
    """Тесты для асинхронного клиента Kannel."""

    def test_init(self):
        """Тест инициализации клиента."""
        client = AsyncKannel("test", "test")
        assert client.username == "test"
        assert client.password == "test"
        assert client.url == "http://localhost:13013"
        assert client.source == "SMS Aero"

    def test_init_with_custom_params(self):
        """Тест инициализации с пользовательскими параметрами."""
        client = AsyncKannel(
            "test",
            "test",
            url="http://test.com",
            source="Test",
            timeout=10.0,
            retry_max_attempts=3,
            retry_delay=2.0,
            retry_backoff=3.0,
        )
        assert client.url == "http://test.com"
        assert client.source == "Test"
        assert client.timeout == 10.0
        assert client.retry_max_attempts == 3
        assert client.retry_delay == 2.0
        assert client.retry_backoff == 3.0

    def test_init_empty_credentials(self):
        """Тест инициализации с пустыми учетными данными."""
        with pytest.raises(ValueError, match="Имя пользователя и пароль не могут быть пустыми"):
            AsyncKannel("", "")

    def test_init_invalid_url(self):
        """Тест инициализации с некорректным URL."""
        with pytest.raises(ValueError, match="Некорректный URL"):
            AsyncKannel("test", "test", url="invalid")

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_check_connection_success(self, mock_get):
        """Тест успешной проверки соединения."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_get.return_value.__aenter__.return_value = mock_response

        client = AsyncKannel("test", "test")
        assert await client.check_connection() is True

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_check_connection_failure(self, mock_get):
        """Тест неудачной проверки соединения."""
        mock_get.side_effect = aiohttp.ClientError()

        client = AsyncKannel("test", "test")
        assert await client.check_connection() is False

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_send_sms_success(self, mock_get):
        """Тест успешной отправки SMS."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="0: Accepted for delivery")
        mock_get.return_value.__aenter__.return_value = mock_response

        client = AsyncKannel("test", "test")
        result = await client.send_sms("+79001234567", "Test message")

        assert result["status"] == "accepted"
        assert result["response"] == "0: Accepted for delivery"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_send_sms_queued(self, mock_get):
        """Тест отправки SMS в очередь."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="3: Queued for delivery")
        mock_get.return_value.__aenter__.return_value = mock_response

        client = AsyncKannel("test", "test")
        result = await client.send_sms("+79001234567", "Test message")

        assert result["status"] == "queued"
        assert result["response"] == "3: Queued for delivery"

    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.get")
    async def test_send_sms_error(self, mock_get):
        """Тест ошибки отправки SMS."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="1: Error message")
        mock_get.return_value.__aenter__.return_value = mock_response

        client = AsyncKannel("test", "test")
        with pytest.raises(KannelConnectionError, match="Ошибка отправки SMS: 1: Error message"):
            await client.send_sms("+79001234567", "Test message")

    @pytest.mark.asyncio
    async def test_send_sms_empty_message(self):
        """Тест отправки пустого сообщения."""
        client = AsyncKannel("test", "test")
        with pytest.raises(ValueError, match="Текст сообщения не может быть пустым"):
            await client.send_sms("+79001234567", "")

    @pytest.mark.asyncio
    async def test_send_sms_invalid_phone(self):
        """Тест отправки на некорректный номер."""
        client = AsyncKannel("test", "test")
        with pytest.raises(ValueError, match="Ошибка парсинга номера телефона"):
            await client.send_sms("invalid", "Test message")
