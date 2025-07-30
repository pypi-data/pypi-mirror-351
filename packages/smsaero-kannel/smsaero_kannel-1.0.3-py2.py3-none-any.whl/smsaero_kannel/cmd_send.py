"""
Модуль для отправки SMS через командную строку.
"""

import argparse
import asyncio
import logging
import sys

from .async_kannel import AsyncKannel
from .constants import (
    DEFAULT_CODING,
    CODING_UCS2,
    CODING_8BIT,
    DEFAULT_DLR_MASK,
    DLR_MASK_NONE,
    DLR_MASK_SUCCESS,
    DLR_MASK_FAILURE,
    DLR_MASK_INTERMEDIATE,
)
from .errors import KannelError
from .logging import setup_logging
from .dlr_server import DLRServer

logger = logging.getLogger(__name__)

# Статусы доставки
DELIVERY_STATUSES = {
    "4": "ACCEPTED",  # Сообщение принято SMSC
    "8": "QUEUED",  # В очереди на отправку
    "16": "SENT",  # Отправлено
    "1": "DELIVERED",  # Доставлено
    "0": "FAILED",  # Ошибка доставки
}

# Финальные статусы
FINAL_STATUSES = ["1", "0"]  # DELIVERED или FAILED


def parse_args() -> argparse.Namespace:
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Отправка SMS через Kannel")
    parser.add_argument("--username", required=True, help="Имя пользователя Kannel")
    parser.add_argument("--password", required=True, help="Пароль Kannel")
    parser.add_argument("--url", default=AsyncKannel.DEFAULT_URL, help="URL Kannel сервера")
    parser.add_argument("--source", default=AsyncKannel.DEFAULT_SOURCE, help="Номер отправителя")
    parser.add_argument("--phone", required=True, help="Номер телефона получателя")
    parser.add_argument("--message", required=True, help="Текст сообщения")
    parser.add_argument(
        "--coding",
        type=int,
        default=DEFAULT_CODING,
        choices=[DEFAULT_CODING, CODING_8BIT, CODING_UCS2],
        help="Кодировка сообщения",
    )
    parser.add_argument("--dlr-url", help="URL для получения статусов доставки")
    parser.add_argument(
        "--dlr-mask",
        type=int,
        default=DEFAULT_DLR_MASK,
        choices=[DLR_MASK_NONE, DLR_MASK_SUCCESS, DLR_MASK_FAILURE, DLR_MASK_INTERMEDIATE, DEFAULT_DLR_MASK],
        help="Маска DLR",
    )
    parser.add_argument("--account", help="Идентификатор аккаунта")
    parser.add_argument("--dlr-host", default="0.0.0.0", help="Хост для прослушивания DLR сервера")
    parser.add_argument("--dlr-port", type=int, default=5555, help="Порт для прослушивания DLR сервера")
    parser.add_argument("--debug", action="store_true", help="Включить отладочный режим")
    return parser.parse_args()


async def send_sms(args: argparse.Namespace) -> None:
    """Отправка SMS с заданными параметрами."""
    dlr_server = None
    try:
        # Создаем DLR сервер только если указан dlr-url
        if args.dlr_url:
            dlr_server = DLRServer(host=args.dlr_host, port=args.dlr_port)
            dlr_received = asyncio.Event()  # Событие для ожидания DLR
            final_status = [None]  # Список для хранения финального статуса

            def dlr_callback(status: str) -> None:
                """Callback для обработки DLR."""
                status_text = DELIVERY_STATUSES.get(status, f"Неизвестный статус ({status})")
                print(f"Получен DLR статус: {status_text}")
                if status in FINAL_STATUSES:
                    final_status[0] = status
                    dlr_received.set()

            await dlr_server.start(dlr_callback)

        async with AsyncKannel(
            username=args.username,
            password=args.password,
            url=args.url,
            source=args.source,
        ) as client:
            # Формируем параметры для отправки
            sms_params = {
                "phone": args.phone,
                "message": args.message,
                "coding": args.coding,
                "dlr_mask": args.dlr_mask,
                "account": args.account,
            }

            # Добавляем dlr_url только если он указан
            if args.dlr_url:
                # Если в URL нет параметров, добавляем параметры по умолчанию
                if "?" not in args.dlr_url:
                    sms_params["dlr_url"] = f"{args.dlr_url}?id=%i&status=%d&response=%A&smsc=%i&from=%f&to=%p"
                else:
                    sms_params["dlr_url"] = args.dlr_url

            # Отправляем SMS
            result = await client.send_sms(**sms_params)
            print(f"Статус отправки: {result['status']}")
            if result.get("message_id"):
                print(f"ID сообщения: {result['message_id']}")
            print(f"Ответ: {result['response']}")

            # Если запущен DLR сервер, ждем DLR
            if dlr_server:
                print("Ожидание DLR...")
                try:
                    # Ждем DLR с таймаутом 30 секунд
                    await asyncio.wait_for(dlr_received.wait(), timeout=30.0)
                    if final_status[0]:
                        status_text = DELIVERY_STATUSES.get(final_status[0], f"Неизвестный статус ({final_status[0]})")
                        print(f"Финальный статус доставки: {status_text}")
                    else:
                        print("Время ожидания DLR истекло")
                except asyncio.TimeoutError:
                    print("Время ожидания DLR истекло")

    except KannelError as e:
        print(f"Ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        if dlr_server:
            await dlr_server.stop()


def main() -> None:
    """Основная функция."""
    args = parse_args()

    # Настройка логирования
    log_level = logging.DEBUG if args.debug else logging.CRITICAL
    setup_logging(level=log_level)

    # Запуск отправки SMS
    asyncio.run(send_sms(args))


if __name__ == "__main__":
    main()
