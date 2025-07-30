"""
Модуль с исключениями для Kannel.
"""


class KannelError(Exception):
    """Базовый класс для исключений Kannel."""

    def __init__(self, message: str = "Ошибка Kannel"):
        super().__init__(message)


class KannelConnectionError(KannelError):
    """Исключение при ошибке подключения к Kannel серверу."""

    def __init__(self, message: str = "Ошибка подключения к Kannel серверу"):
        super().__init__(message)


class KannelValidationError(KannelError):
    """Исключение при ошибке валидации данных."""

    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(message)


class KannelConfigError(KannelError):
    """Исключение при ошибке конфигурации."""


class KannelResponseError(KannelError):
    """Исключение при ошибке ответа от Kannel сервера."""


class RetryError(KannelError):
    """Исключение, возникающее при превышении максимального количества попыток."""

    def __init__(self, message: str = "Превышено максимальное количество попыток"):
        super().__init__(message)


class KannelRetryError(KannelError):
    """Исключение при ошибке повторных попыток."""
