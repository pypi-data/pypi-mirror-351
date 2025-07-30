"""
Тесты для механизма повторных попыток.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from smsaero_kannel.retry import retry, RetryError


class TestRetry:
    """Тесты для механизма повторных попыток."""

    def test_retry_success(self):
        """Тест успешного выполнения без повторных попыток."""
        mock_func = MagicMock(return_value="success")
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_success_after_failures(self):
        """Тест успешного выполнения после нескольких неудач."""
        mock_func = MagicMock(side_effect=[Exception, Exception, "success"])
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_max_attempts_exceeded(self):
        """Тест превышения максимального количества попыток."""
        mock_func = MagicMock(side_effect=Exception)
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        with pytest.raises(RetryError):
            decorated()
        assert mock_func.call_count == 3

    def test_retry_with_custom_exceptions(self):
        """Тест с пользовательскими исключениями."""
        mock_func = MagicMock(side_effect=[ValueError, TypeError, "success"])
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(ValueError, TypeError))(mock_func)
        result = decorated()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_with_unexpected_exception(self):
        """Тест с непредвиденным исключением."""
        mock_func = MagicMock(side_effect=RuntimeError)
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(ValueError, TypeError))(mock_func)
        with pytest.raises(RuntimeError):
            decorated()
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry_success(self):
        """Тест успешного выполнения асинхронной функции без повторных попыток."""
        mock_func = AsyncMock(return_value="success")
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        result = await decorated()
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_async_retry_success_after_failures(self):
        """Тест успешного выполнения асинхронной функции после нескольких неудач."""
        mock_func = AsyncMock(side_effect=[Exception, Exception, "success"])
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        result = await decorated()
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_max_attempts_exceeded(self):
        """Тест превышения максимального количества попыток для асинхронной функции."""
        mock_func = AsyncMock(side_effect=Exception)
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)
        with pytest.raises(RetryError):
            await decorated()
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_with_custom_exceptions(self):
        """Тест с пользовательскими исключениями для асинхронной функции."""
        mock_func = AsyncMock(side_effect=[ValueError, TypeError, "success"])
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(ValueError, TypeError))(mock_func)
        result = await decorated()
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_with_unexpected_exception(self):
        """Тест с непредвиденным исключением для асинхронной функции."""
        mock_func = AsyncMock(side_effect=RuntimeError)
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(ValueError, TypeError))(mock_func)
        with pytest.raises(RuntimeError):
            await decorated()
        assert mock_func.call_count == 1
