"""
Асинхронный модуль для работы с Kannel HTTP API.
"""

import logging
import typing
from urllib.parse import urljoin

import aiohttp

from .constants import (
    DEFAULT_CODING,
    DEFAULT_DLR_MASK,
    DEFAULT_CHARSET,
)
from .errors import KannelConnectionError
from .validators import validate_phone, validate_url, validate_message
from .retry import retry

logger = logging.getLogger(__name__)


class AsyncKannel:
    """Асинхронный класс для отправки SMS через Kannel HTTP API."""

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
        Инициализация асинхронного клиента Kannel.

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
        self._session: typing.Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Создает сессию при входе в контекстный менеджер."""
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрывает сессию при выходе из контекстного менеджера."""
        if self._session:
            await self._session.close()
            self._session = None

    def _get_retry_decorator(self):
        """Создает декоратор retry с текущими настройками."""
        if self.retry_max_attempts <= 1:
            return lambda func: func
        return retry(max_attempts=self.retry_max_attempts, delay=self.retry_delay, backoff=self.retry_backoff)

    @property
    def send_sms(self):
        """Метод отправки SMS с текущими настройками retry."""
        return self._get_retry_decorator()(self._send_sms)

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Создает сессию, если она еще не создана."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    async def _send_sms(
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
            # Валидация входных данных
            validated_phone = validate_phone(phone)
            validated_message = validate_message(message)

            # Формирование параметров запроса
            request_params = {
                "username": self.username,
                "password": self.password,
                "coding": coding,
                "charset": DEFAULT_CHARSET,
                "from": self.source,
                "to": validated_phone,
                "text": validated_message,
                "dlr-mask": dlr_mask,
            }

            # Добавление опциональных параметров
            if dlr_url:
                request_params["dlr-url"] = dlr_url
            if account:
                request_params["account"] = account
            request_params.update(kwargs)

            # Отправка запроса
            session = await self._ensure_session()
            send_url = urljoin(self.url, "cgi-bin/sendsms")
            async with session.get(send_url, params=request_params) as response:
                if response.status not in (200, 201, 202):
                    raise KannelConnectionError(f"Ошибка отправки SMS: {await response.text()}")

                result = (await response.text()).strip()
                if not result.startswith(("0: Accepted", "3: Queued")):
                    raise KannelConnectionError(f"Ошибка отправки SMS: {result}")

                # Обработка успешного ответа
                status = "queued" if result.startswith("3:") else "accepted"
                logger.info("SMS успешно отправлено на: %s", phone)
                return {"status": status, "response": result}

        except aiohttp.ClientError as e:
            logger.error("Ошибка подключения к Kannel серверу: %s", str(e))
            raise KannelConnectionError() from e
        except ValueError as e:
            logger.error("Ошибка валидации: %s", str(e))
            raise
        except Exception as e:
            logger.error("Неожиданная ошибка при отправке SMS: %s", str(e))
            raise

    async def check_connection(self) -> bool:
        """
        Проверяет доступность Kannel сервера.

        Returns:
            bool: True если сервер доступен, False в противном случае
        """
        try:
            session = await self._ensure_session()
            async with session.get(self.url) as response:
                return response.status == 200
        except aiohttp.ClientError:
            return False
