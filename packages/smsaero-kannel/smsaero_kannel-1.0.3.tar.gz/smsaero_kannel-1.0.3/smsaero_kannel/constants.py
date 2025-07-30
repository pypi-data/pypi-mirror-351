"""
Константы для работы с Kannel.
"""

# Кодировки сообщений
CODING_GSM7 = 0  # GSM 7-bit
CODING_8BIT = 1  # 8-bit
CODING_UCS2 = 2  # UCS2 (UTF-16)

# Кодировка по умолчанию
DEFAULT_CODING = CODING_UCS2  # UCS2 для поддержки Unicode

# Кодировка по умолчанию
DEFAULT_CHARSET = "UTF-8"  # Кодировка по умолчанию

# Маски DLR
DLR_MASK_NONE = 0  # Без DLR
DLR_MASK_SUCCESS = 1  # Только успешная доставка
DLR_MASK_FAILURE = 2  # Только ошибки
DLR_MASK_INTERMEDIATE = 4  # Промежуточные статусы
DEFAULT_DLR_MASK = 31  # Все статусы

# Маппинг статусов
STATUS_MAPPING = {
    "0: Accepted": "accepted",
    "0: Accepted for delivery": "accepted",
    "3: Queued": "queued",
    "4: Sent": "sent",
    "8: Delivered": "delivered",
    "16: Failed": "failed",
}

# Финальные статусы
FINAL_STATUSES = ["delivered", "failed"]
