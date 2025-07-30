"""
Модуль с валидаторами для Kannel.
"""

from urllib.parse import urlparse

from phonenumbers import parse, NumberParseException


def validate_phone(phone: str) -> str:
    """
    Валидирует номер телефона.

    Args:
        phone: Номер телефона в международном формате

    Returns:
        str: Валидный номер телефона

    Raises:
        ValueError: При некорректном номере телефона
    """
    try:
        parsed_number = parse(phone, None)
        if not parsed_number:
            raise ValueError("Ошибка парсинга номера телефона")
        return f"+{parsed_number.country_code}{parsed_number.national_number}"
    except NumberParseException as e:
        raise ValueError(f"Ошибка парсинга номера телефона: {str(e)}") from e


def validate_message(message: str) -> str:
    """
    Валидирует текст сообщения.

    Args:
        message: Текст сообщения

    Returns:
        str: Валидный текст сообщения

    Raises:
        ValueError: При пустом сообщении
    """
    if not message or not message.strip():
        raise ValueError("Текст сообщения не может быть пустым")
    return message


def validate_url(url: str) -> str:
    """
    Валидирует URL.

    Args:
        url: URL для валидации

    Returns:
        str: Валидный URL

    Raises:
        ValueError: При некорректном URL
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Некорректный URL")
        return url.rstrip("/")
    except Exception as e:
        raise ValueError(f"Ошибка валидации URL: {str(e)}") from e


def validate_coding(coding: int) -> int:
    """
    Валидация кодировки сообщения.

    Args:
        coding: Код кодировки

    Returns:
        int: Валидный код кодировки

    Raises:
        ValueError: При некорректном коде кодировки
    """
    valid_codings = {0, 1, 8}  # GSM 7-bit, 8-bit, UCS2
    if coding not in valid_codings:
        raise ValueError(f"Некорректный код кодировки. Допустимые значения: {valid_codings}")

    return coding


def validate_dlr_mask(mask: int) -> int:
    """
    Валидация маски DLR.

    Args:
        mask: Маска DLR

    Returns:
        int: Валидная маска DLR

    Raises:
        ValueError: При некорректной маске DLR
    """
    if not isinstance(mask, int) or mask < 0 or mask > 31:
        raise ValueError("Маска DLR должна быть числом от 0 до 31")

    return mask
