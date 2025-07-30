"""
Настройка логирования для Kannel клиента.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    stream: Optional[logging.StreamHandler] = None,
) -> None:
    """
    Настройка логирования.

    Args:
        level: Уровень логирования
        format_string: Строка форматирования логов
        stream: Поток для вывода логов
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if stream is None:
        stream = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(format_string)
    stream.setFormatter(formatter)

    logger = logging.getLogger("smsaero_kannel")
    logger.setLevel(level)
    logger.addHandler(stream)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Получение логгера.

    Args:
        name: Имя логгера

    Returns:
        logging.Logger: Настроенный логгер
    """
    if name is None:
        name = "smsaero_kannel"

    return logging.getLogger(name)
