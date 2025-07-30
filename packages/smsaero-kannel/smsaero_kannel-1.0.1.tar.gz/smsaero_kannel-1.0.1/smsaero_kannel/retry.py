"""
Модуль для механизма повторных попыток.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Optional, Type, Union, Tuple, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryError(Exception):
    """Исключение, возникающее при превышении максимального количества попыток."""

    def __init__(self, message: str = "Превышено максимальное количество попыток"):
        super().__init__(message)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
) -> Callable:
    """
    Декоратор для повторных попыток выполнения функции.

    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками в секундах
        backoff: Множитель для увеличения задержки
        exceptions: Исключения, при которых нужно повторять попытки

    Returns:
        Callable: Декорированная функция
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            "Попытка %d из %d не удалась: %s. Повторная попытка через %.1f сек.",
                            attempt + 1,
                            max_attempts,
                            str(e),
                            current_delay,
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error("Все %d попыток не удались. Последняя ошибка: %s", max_attempts, str(e))
                        raise RetryError(f"Превышено максимальное количество попыток: {str(e)}") from e

            if last_exception:
                raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            "Попытка %d из %d не удалась: %s. Повторная попытка через %.1f сек.",
                            attempt + 1,
                            max_attempts,
                            str(e),
                            current_delay,
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error("Все %d попыток не удались. Последняя ошибка: %s", max_attempts, str(e))
                        raise RetryError(f"Превышено максимальное количество попыток: {str(e)}") from e

            if last_exception:
                raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[type, tuple[type, ...]] = Exception,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Декоратор для повторных попыток выполнения асинхронной функции.

    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками в секундах
        backoff: Множитель для увеличения задержки
        exceptions: Исключения, при которых нужно повторять попытку

    Returns:
        Callable: Декорированная асинхронная функция
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            "Попытка %d из %d не удалась: %s. Повторная попытка через %.1f секунд",
                            attempt + 1,
                            max_attempts,
                            str(e),
                            current_delay,
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "Все %d попыток не удались. Последняя ошибка: %s",
                            max_attempts,
                            str(e),
                        )

            if last_exception:
                raise last_exception
            return None  # type: ignore

        return wrapper

    return decorator
