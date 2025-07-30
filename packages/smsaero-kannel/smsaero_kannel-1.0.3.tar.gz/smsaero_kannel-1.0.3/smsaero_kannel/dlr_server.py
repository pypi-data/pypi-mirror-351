"""
Модуль для работы с DLR сервером.
"""

import logging
from typing import Callable, Optional

from aiohttp import web

logger = logging.getLogger(__name__)


class DLRServer:
    """Сервер для получения DLR."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Инициализация DLR сервера.

        Args:
            host: Хост для прослушивания
            port: Порт для прослушивания
        """
        self.host = host
        self.port = port
        self._app = web.Application()
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._status_callback: Optional[Callable[[str], None]] = None

    @property
    def dlr_url(self) -> str:
        """URL для получения DLR."""
        return f"http://{self.host}:{self.port}/dlr"

    async def start(self, status_callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Запуск DLR сервера.

        Args:
            status_callback: Функция обратного вызова для обработки статусов
        """
        self._status_callback = status_callback
        self._app.router.add_get("/dlr", self.handle_dlr)
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()
        logger.info("DLR сервер запущен на %s:%d", self.host, self.port)

    async def stop(self) -> None:
        """Остановка DLR сервера."""
        if self._runner:
            await self._runner.cleanup()
            logger.info("DLR сервер остановлен")

    async def handle_dlr(self, request: web.Request) -> web.Response:
        """
        Обработка DLR запроса.

        Args:
            request: HTTP запрос

        Returns:
            web.Response: HTTP ответ
        """
        try:
            params = request.query
            if "status" not in params:
                logger.warning("Получен DLR запрос без статуса")
                return web.Response(status=400, text="Missing status parameter")

            status = params["status"]
            logger.info("Получен DLR запрос со статусом: %s", status)

            if self._status_callback:
                try:
                    self._status_callback(status)
                except (ValueError, TypeError) as e:
                    logger.error("Ошибка в callback функции: %s", str(e))
                    return web.Response(status=500, text="Callback error")

            return web.Response(text="OK")

        except (ValueError, TypeError) as e:
            logger.error("Ошибка обработки DLR запроса: %s", str(e))
            return web.Response(status=500, text="Internal server error")
