"""
Типы данных для работы с Kannel.
"""

import dataclasses
from typing import Optional, Dict, Any


@dataclasses.dataclass
class MessageInfo:
    """Информация о сообщении."""

    message_id: Optional[str]
    status: str
    final: bool
    response: str
    error_code: Optional[int] = None


@dataclasses.dataclass
class SendSmsResult:
    """Результат отправки SMS."""

    status: str
    message_id: Optional[str]
    response: str
    parts_count: Optional[int] = None


@dataclasses.dataclass
class SmsStatusResult:
    """Результат проверки статуса SMS."""

    message_id: str
    status: str
    final: bool
    response: str
    error_code: Optional[int] = None


@dataclasses.dataclass
class KannelConfig:
    """Конфигурация Kannel клиента."""

    username: str
    password: str
    url: str
    source: str
    timeout: float
    retry_max_attempts: int
    retry_delay: float
    retry_backoff: float

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует конфигурацию в словарь."""
        return {
            "username": self.username,
            "password": self.password,
            "url": self.url,
            "source": self.source,
            "timeout": self.timeout,
            "retry_max_attempts": self.retry_max_attempts,
            "retry_delay": self.retry_delay,
            "retry_backoff": self.retry_backoff,
        }
