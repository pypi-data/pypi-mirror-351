"""
Команда для эмуляции Kannel сервера.
"""

import argparse
import asyncio
import logging
import random
import time
from datetime import datetime
from typing import Dict
from urllib.parse import urlparse, parse_qs, urlencode

import aiohttp
from aiohttp import web

logger = logging.getLogger(__name__)

# Статусы доставки и их последовательность
DELIVERY_STATUSES = [
    "4",  # ACCEPTED - Сообщение принято SMSC
    "8",  # QUEUED - В очереди на отправку
    "16",  # SENT - Отправлено
    "1",  # DELIVERED - Доставлено
    "0",  # FAILED - Ошибка доставки
]

# Маски DLR
DLR_MASKS = {
    0: [],  # Без DLR
    1: ["1"],  # Только успешная доставка
    2: ["0"],  # Только ошибки
    4: ["4", "8", "16"],  # Промежуточные статусы
    31: DELIVERY_STATUSES,  # Все статусы
}

# Эскейп-коды для DLR URL
ESCAPE_CODES = {
    "p": "phone",  # Номер телефона получателя
    "P": "phone",  # Номер телефона отправителя
    "i": "message_id",  # ID сообщения
    "I": "message_id",  # ID сообщения
    "q": "queue_id",  # ID очереди
    "a": "account",  # Имя аккаунта
    "A": "account",  # Имя аккаунта
    "b": "boxc_id",  # ID бокса
    "B": "boxc_id",  # ID бокса
    "t": "timestamp",  # Временная метка
    "T": "timestamp",  # Временная метка
    "n": "n",  # Номер попытки
    "N": "n",  # Номер попытки
    "M": "meta_data",  # Метаданные
    "m": "meta_data",  # Метаданные
    "c": "coding",  # Кодировка
    "C": "coding",  # Кодировка
    "r": "charset",  # Кодировка
    "R": "charset",  # Кодировка
    "D": "dlr_mask",  # Маска DLR
    "d": "status",  # Статус доставки
    "S": "smsc_id",  # ID SMSC
    "s": "smsc_id",  # ID SMSC
    "u": "username",  # Имя пользователя
    "U": "username",  # Имя пользователя
    "h": "smsc_username",  # Имя пользователя SMSC
    "H": "smsc_username",  # Имя пользователя SMSC
    "f": "from",  # Отправитель
    "F": "from",  # Отправитель
    "k": "to",  # Получатель
    "K": "to",  # Получатель
    "l": "smsc_priority",  # Приоритет SMSC
    "L": "smsc_priority",  # Приоритет SMSC
    "o": "smsc_timeout",  # Таймаут SMSC
    "O": "smsc_timeout",  # Таймаут SMSC
    "v": "validity",  # Время жизни
    "V": "validity",  # Время жизни
    "e": "deferred",  # Отложенная отправка
    "E": "deferred",  # Отложенная отправка
    "y": "dlr_url",  # URL для DLR
    "Y": "dlr_url",  # URL для DLR
    "x": "x",  # X-параметр
    "X": "x",  # X-параметр
    "w": "w",  # W-параметр
    "W": "w",  # W-параметр
    "z": "z",  # Z-параметр
    "Z": "z",  # Z-параметр
}


class KannelEmulator:
    """Эмулятор Kannel сервера."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 13013,
        username: str = "test",
        password: str = "test",
        delay: float = 1.0,
        random_delay: bool = False,
    ):
        """
        Инициализация эмулятора Kannel.

        Args:
            host: Хост для прослушивания
            port: Порт для прослушивания
            username: Имя пользователя для аутентификации
            password: Пароль для аутентификации
            delay: Задержка между статусами в секундах
            random_delay: Использовать случайную задержку
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.delay = delay
        self.random_delay = random_delay
        self.app = web.Application()
        self.app.router.add_get("/cgi-bin/sendsms", self.handle_send_sms)
        self.app.router.add_get("/cgi-bin/query_sm", self.handle_query_sm)
        self.messages = {}  # Хранилище сообщений

    async def start(self):
        """Запуск эмулятора."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info("Kannel эмулятор запущен на http://%s:%d", self.host, self.port)
        return runner

    def _validate_credentials(self, username: str, password: str) -> bool:
        """Проверка учетных данных."""
        return username == self.username and password == self.password

    def _generate_message_id(self) -> str:
        """Генерация уникального ID сообщения."""
        return f"{int(time.time())}{random.randint(1000, 9999)}"

    def _get_delay(self) -> float:
        """Получение задержки между статусами."""
        if self.random_delay:
            return random.uniform(0.5, self.delay * 2)
        return self.delay

    def _format_dlr_url(self, dlr_url: str, params: Dict) -> str:
        """
        Форматирование DLR URL с учетом эскейп-кодов.

        Args:
            dlr_url: Исходный URL для DLR
            params: Параметры сообщения

        Returns:
            str: Отформатированный URL
        """
        if not dlr_url:
            return ""

        # Парсим URL и параметры
        parsed = urlparse(dlr_url)
        query = parse_qs(parsed.query)
        path = parsed.path

        # Заменяем эскейп-коды в пути
        for code, param in ESCAPE_CODES.items():
            if param in params:
                path = path.replace(f"%{code}", str(params[param]))

        # Заменяем эскейп-коды в параметрах
        new_query = {}
        for key, values in query.items():
            new_values = []
            for value in values:
                for code, param in ESCAPE_CODES.items():
                    if param in params:
                        value = value.replace(f"%{code}", str(params[param]))
                new_values.append(value)
            new_query[key] = new_values

        # Формируем новый URL
        new_url = parsed._replace(path=path, query=urlencode(new_query, doseq=True)).geturl()

        return new_url

    async def handle_send_sms(self, request: web.Request) -> web.Response:
        """Обработка запроса на отправку SMS."""
        # Получаем параметры
        params = dict(request.query)

        # Проверяем учетные данные
        if not self._validate_credentials(params.get("username"), params.get("password")):
            return web.Response(text="Error: Invalid credentials", status=401)

        # Проверяем обязательные параметры
        if not all(key in params for key in ["to", "text"]):
            return web.Response(text="Error: Missing required parameters", status=400)

        # Генерируем ID сообщения
        message_id = self._generate_message_id()

        # Сохраняем информацию о сообщении
        self.messages[message_id] = {
            "message_id": message_id,
            "to": params["to"],
            "from": params.get("from", ""),
            "text": params["text"],
            "coding": int(params.get("coding", 0)),
            "dlr_url": params.get("dlr-url"),
            "dlr_mask": int(params.get("dlr-mask", 31)),
            "account": params.get("account"),
            "timestamp": datetime.now().isoformat(),
            "status": "4",  # Начинаем с ACCEPTED
            "current_status_index": 0,
        }

        # Запускаем асинхронную задачу для отправки DLR
        asyncio.create_task(self._send_dlr_updates(message_id))

        # Возвращаем успешный ответ
        return web.Response(text=f"0: Accepted for delivery [{message_id}]")

    async def handle_query_sm(self, request: web.Request) -> web.Response:
        """Обработка запроса на проверку статуса SMS."""
        # Получаем параметры
        params = dict(request.query)

        # Проверяем учетные данные
        if not self._validate_credentials(params.get("username"), params.get("password")):
            return web.Response(text="Error: Invalid credentials", status=401)

        # Проверяем ID сообщения
        message_id = params.get("message_id")
        if not message_id or message_id not in self.messages:
            return web.Response(text="Error: Message not found", status=404)

        # Возвращаем текущий статус
        return web.Response(text=self.messages[message_id]["status"])

    async def _send_dlr_updates(self, message_id: str):
        """
        Отправка обновлений статуса DLR.

        Args:
            message_id: ID сообщения
        """
        message = self.messages[message_id]
        dlr_mask = message["dlr_mask"]
        dlr_url = message["dlr_url"]

        if not dlr_url or not dlr_mask:
            return

        # Получаем список статусов для отправки
        statuses = DLR_MASKS.get(dlr_mask, [])
        if not statuses:
            return

        # Отправляем статусы
        async with aiohttp.ClientSession() as session:
            for status in statuses:
                # Обновляем статус сообщения
                message["status"] = status
                message["current_status_index"] = DELIVERY_STATUSES.index(status)

                # Формируем URL с параметрами
                dlr_params = {
                    "message_id": message_id,
                    "phone": message["to"],
                    "from": message["from"],
                    "status": status,  # Отправляем текущий статус
                    "timestamp": datetime.now().isoformat(),
                    "account": message["account"],
                    "coding": message["coding"],
                }

                # Форматируем URL
                formatted_url = self._format_dlr_url(dlr_url, dlr_params)
                if not formatted_url:
                    continue

                try:
                    # Отправляем DLR без SSL
                    async with session.get(formatted_url, ssl=False) as response:
                        if response.status != 200:
                            logger.error("Ошибка отправки DLR: %d", response.status)
                            logger.error("URL: %s", formatted_url)
                            logger.error("Параметры: %s", dlr_params)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.error("Ошибка отправки DLR: %s", str(e))
                    logger.error("URL: %s", formatted_url)
                    logger.error("Параметры: %s", dlr_params)

                # Ждем перед следующим статусом
                await asyncio.sleep(self._get_delay())


async def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Эмулятор Kannel сервера")
    parser.add_argument("--host", default="localhost", help="Хост для прослушивания")
    parser.add_argument("--port", type=int, default=13013, help="Порт для прослушивания")
    parser.add_argument("--username", default="test", help="Имя пользователя")
    parser.add_argument("--password", default="test", help="Пароль")
    parser.add_argument("--delay", type=float, default=1.0, help="Задержка между статусами в секундах")
    parser.add_argument("--random-delay", action="store_true", help="Использовать случайную задержку")
    args = parser.parse_args()

    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Создаем и запускаем эмулятор
    emulator = KannelEmulator(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        delay=args.delay,
        random_delay=args.random_delay,
    )
    runner = await emulator.start()

    try:
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Остановка эмулятора...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
