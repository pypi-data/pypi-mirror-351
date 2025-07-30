"""
Тесты для основного клиента Kannel.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock

from smsaero_kannel.kannel import Kannel
from smsaero_kannel.errors import KannelConnectionError


class TestKannel:
    """Тесты для основного клиента Kannel."""

    def test_init(self):
        """Тест инициализации клиента."""
        client = Kannel("test", "test")
        assert client.username == "test"
        assert client.password == "test"
        assert client.url == "http://localhost:13013"
        assert client.source == "SMS Aero"

    def test_init_with_custom_params(self):
        """Тест инициализации с пользовательскими параметрами."""
        client = Kannel(
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

    def test_init_with_empty_credentials(self):
        """Тест инициализации с пустыми учетными данными."""
        with pytest.raises(ValueError, match="Имя пользователя и пароль не могут быть пустыми"):
            Kannel("", "test")
        with pytest.raises(ValueError, match="Имя пользователя и пароль не могут быть пустыми"):
            Kannel("test", "")

    @patch("requests.get")
    def test_check_connection_success(self, mock_get):
        """Тест успешной проверки соединения."""
        mock_get.return_value.status_code = 200
        client = Kannel("test", "test")
        assert client.check_connection() is True

    @patch("requests.get")
    def test_check_connection_failure(self, mock_get):
        """Тест неудачной проверки соединения."""
        mock_get.side_effect = requests.RequestException()
        client = Kannel("test", "test")
        assert client.check_connection() is False

    @patch("requests.get")
    def test_send_sms_success(self, mock_get):
        """Тест успешной отправки SMS."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "0: Accepted for delivery [17486793049268]"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        result = client.send_sms("+79001234567", "Test message")

        assert result["status"] == "accepted"
        assert result["message_id"] == "[17486793049268]"

    @patch("requests.get")
    def test_send_sms_queued(self, mock_get):
        """Тест отправки SMS в очередь."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "3: Queued for delivery [17486793049268]"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        result = client.send_sms("+79001234567", "Test message")

        assert result["status"] == "queued"
        assert result["message_id"] == "[17486793049268]"

    @patch("requests.get")
    def test_send_sms_error(self, mock_get):
        """Тест ошибки отправки SMS."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1: Error message"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        with pytest.raises(KannelConnectionError, match="Ошибка отправки SMS: 1: Error message"):
            client.send_sms("+79001234567", "Test message")

    def test_send_sms_empty_message(self):
        """Тест отправки пустого сообщения."""
        client = Kannel("test", "test")
        with pytest.raises(ValueError, match="Текст сообщения не может быть пустым"):
            client.send_sms("+79001234567", "")

    def test_send_sms_invalid_phone(self):
        """Тест отправки на некорректный номер."""
        client = Kannel("test", "test")
        with pytest.raises(ValueError, match="Ошибка парсинга номера телефона"):
            client.send_sms("invalid", "Test message")

    @patch("requests.get")
    def test_sms_status_success(self, mock_get):
        """Тест успешной проверки статуса."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "0: Delivered"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        result = client.sms_status("17486793049268")

        assert result["status"] == "unknown"
        assert result["final"] is False

    @patch("requests.get")
    def test_sms_status_unknown(self, mock_get):
        """Тест проверки неизвестного статуса."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Unknown status"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        result = client.sms_status("17486793049268")

        assert result["status"] == "unknown"
        assert result["final"] is False

    @patch("requests.get")
    def test_sms_status_error(self, mock_get):
        """Тест ошибки проверки статуса."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        client = Kannel("test", "test")
        with pytest.raises(KannelConnectionError, match="Ошибка получения статуса: Internal Server Error"):
            client.sms_status("17486793049268")
