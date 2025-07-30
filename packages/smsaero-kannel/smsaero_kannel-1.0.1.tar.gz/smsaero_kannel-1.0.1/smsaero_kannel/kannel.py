"""
Основной модуль для работы с Kannel HTTP API.
"""

import logging
import typing
from urllib.parse import urljoin

import requests

from .constants import (
    STATUS_MAPPING,
    FINAL_STATUSES,
    DEFAULT_CODING,
    DEFAULT_DLR_MASK,
    DEFAULT_CHARSET,
)
from .errors import KannelConnectionError
from .validators import validate_phone, validate_url, validate_message
from .retry import retry

logger = logging.getLogger(__name__)


class Kannel:
    """Класс для отправки SMS через Kannel HTTP API."""

    DEFAULT_URL = "http://localhost:13013/"
    DEFAULT_SOURCE = "SMS Aero"
    DEFAULT_RETRY_MAX_ATTEMPTS = 1
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_RETRY_BACKOFF = 2.0

    def __init__(
        self,
        username: str,
        password: str,
        url: str = DEFAULT_URL,
        source: str = DEFAULT_SOURCE,
        timeout: float = 30.0,
        retry_max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
    ):
        """
        Инициализация клиента Kannel.

        Args:
            username: Имя пользователя для Kannel
            password: Пароль для Kannel
            url: URL Kannel сервера
            source: Номер отправителя
            timeout: Тайм-аут для операций с Kannel сервером
            retry_max_attempts: Максимальное количество попыток
            retry_delay: Начальная задержка между попытками в секундах
            retry_backoff: Множитель для увеличения задержки

        Raises:
            ValueError: При некорректных значениях параметров
        """
        if not username or not password:
            raise ValueError("Имя пользователя и пароль не могут быть пустыми")

        self.username = username
        self.password = password
        self.url = validate_url(url)
        self.source = source
        self.timeout = timeout
        self.retry_max_attempts = retry_max_attempts
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff

    def _get_retry_decorator(self):
        """Создает декоратор retry с текущими настройками."""
        if self.retry_max_attempts <= 1:
            return lambda func: func
        return retry(max_attempts=self.retry_max_attempts, delay=self.retry_delay, backoff=self.retry_backoff)

    @property
    def send_sms(self):
        """Метод отправки SMS с текущими настройками retry."""
        return self._get_retry_decorator()(self._send_sms)

    @property
    def sms_status(self):
        """Метод проверки статуса с текущими настройками retry."""
        return self._get_retry_decorator()(self._sms_status)

    def _send_sms(
        self,
        phone: str,
        message: str,
        coding: int = DEFAULT_CODING,
        dlr_url: typing.Optional[str] = None,
        dlr_mask: int = DEFAULT_DLR_MASK,
        account: typing.Optional[str] = None,
        **kwargs,
    ) -> typing.Dict:
        """
        Внутренний метод отправки SMS без retry.

        Args:
            phone: Номер телефона в международном формате
            message: Текст сообщения
            coding: Кодировка сообщения:
                - 0: GSM 7-bit
                - 1: 8-bit
                - 8: UCS2 (UTF-16, по умолчанию)
            dlr_url: URL для получения статусов доставки
            dlr_mask: Маска DLR (Delivery Report):
                - 0: Без DLR
                - 1: Только успешная доставка
                - 2: Только ошибки
                - 4: Промежуточные статусы
                - 31: Все статусы (по умолчанию)
            account: Опциональный идентификатор аккаунта
            **kwargs: Дополнительные параметры Kannel

        Returns:
            dict: Словарь с результатом отправки:
                - status: Статус сообщения ('accepted' или 'queued')
                - message_id: ID сообщения
                - response: Полный ответ от сервера

        Raises:
            KannelConnectionError: При ошибке подключения к серверу
            KannelValidationError: При некорректных входных данных
            ValueError: При ошибке валидации
        """
        logger.info("Попытка отправки SMS на %s", phone)

        try:
            # Валидация и подготовка данных
            validated_data = {
                "phone": validate_phone(phone),
                "message": validate_message(message),
            }

            # Формирование параметров запроса
            request_params = {
                "username": self.username,
                "password": self.password,
                "coding": coding,
                "charset": DEFAULT_CHARSET,
                "from": self.source,
                "to": validated_data["phone"],
                "text": validated_data["message"],
                "dlr-mask": dlr_mask,
            }

            # Добавление опциональных параметров
            if dlr_url:
                request_params["dlr-url"] = dlr_url
            if account:
                request_params["account"] = account
            request_params.update(kwargs)

            # Отправка запроса
            send_url = urljoin(self.url, "cgi-bin/sendsms")
            response = requests.get(send_url, params=request_params, timeout=self.timeout)

            if response.status_code not in (200, 201, 202):
                raise KannelConnectionError(f"Ошибка отправки SMS: {response.text}")

            result = response.text.strip()
            if not result.startswith(("0: Accepted", "3: Queued")):
                raise KannelConnectionError(f"Ошибка отправки SMS: {result}")

            # Обработка успешного ответа
            message_id = result.split(" ")[-1] if len(result.split(" ")) > 2 else None
            status = "queued" if result.startswith("3:") else "accepted"
            logger.info("SMS успешно отправлено на: %s", phone)
            return {"status": status, "message_id": message_id, "response": result}

        except requests.RequestException as e:
            logger.error("Ошибка подключения к Kannel серверу: %s", str(e))
            raise KannelConnectionError() from e
        except ValueError as e:
            logger.error("Ошибка валидации: %s", str(e))
            raise
        except Exception as e:
            logger.error("Неожиданная ошибка при отправке SMS: %s", str(e))
            raise

    def _sms_status(self, message_id: str) -> typing.Dict:
        """
        Внутренний метод проверки статуса без retry.

        Args:
            message_id: ID сообщения для проверки статуса

        Returns:
            dict: Словарь с информацией о статусе:
                - message_id: ID сообщения
                - status: Статус сообщения:
                    - 'accepted': Сообщение принято
                    - 'queued': Сообщение в очереди
                    - 'delivered': Сообщение доставлено
                    - 'failed': Ошибка доставки
                    - 'unknown': Неизвестный статус
                - final: Флаг конечного статуса
                - response: Полный ответ от сервера

        Raises:
            KannelConnectionError: При ошибке подключения к серверу
            ValueError: При пустом message_id
        """
        if not message_id:
            raise ValueError("message_id не может быть пустым")

        logger.info("Запрос статуса для сообщения: %s", message_id)

        try:
            params = {"username": self.username, "password": self.password, "message_id": message_id}

            status_url = urljoin(self.url, "cgi-bin/query_sm")
            response = requests.get(status_url, params=params, timeout=self.timeout)

            if response.status_code != 200:
                raise KannelConnectionError(f"Ошибка получения статуса: {response.text}")

            result = response.text.strip()
            status = STATUS_MAPPING.get(result, "unknown")
            is_final = status in FINAL_STATUSES

            return {"message_id": message_id, "status": status, "final": bool(is_final), "response": result}

        except requests.RequestException as e:
            logger.error("Ошибка подключения к Kannel серверу: %s", str(e))
            raise KannelConnectionError() from e
        except Exception as e:
            logger.error("Ошибка при получении статуса сообщения: %s", str(e))
            raise

    def check_connection(self) -> bool:
        """
        Проверяет доступность Kannel сервера.

        Returns:
            bool: True если сервер доступен, False в противном случае
        """
        try:
            response = requests.get(self.url, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False
