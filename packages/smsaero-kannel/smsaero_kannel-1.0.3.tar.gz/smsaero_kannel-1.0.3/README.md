# Python библиотека для отправки SMS сообщений через Kannel HTTP API

[![PyPI version](https://badge.fury.io/py/smsaero-kannel.svg)](https://badge.fury.io/py/smsaero-kannel)
[![Python Versions](https://img.shields.io/pypi/pyversions/smsaero-kannel.svg)](https://pypi.org/project/smsaero-kannel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](MIT-LICENSE)

## Установка с использованием пакетного менеджера pip:

```bash
pip install smsaero-kannel
```

## Пример использования в коде:

```python
from smsaero_kannel import Kannel, KannelConnectionError, KannelValidationError


# Конфигурация Kannel сервера
KANNEL_USER = 'ваш логин'
KANNEL_PASS = 'ваш пароль'
KANNEL_URL = 'http://localhost:13013/'


def send_sms(phone: str, message: str) -> None:
    """
    Отправка SMS сообщения

    Параметры:
    phone (str): Номер телефона в международном формате.
    message (str): Содержание SMS сообщения.
    """
    client = Kannel(
        username=KANNEL_USER,
        password=KANNEL_PASS,
        url=KANNEL_URL,
        source='SMS Aero',
    )
    
    try:
        result = client.send_sms(
            phone=phone,               # Номер телефона получателя
            message=message,           # Текст сообщения
            coding=0,                  # GSM 7-bit
            dlr_url='http://your-dlr', # URL для получения статусов
            dlr_mask=31,               # Все статусы
            account='account1',        # Опциональный идентификатор аккаунта
            
            ##
            # Дополнительные параметры Kannel
            ##
            priority=1,                # Приоритет сообщения
            validity=1440,             # Время жизни сообщения в минутах
            charset='UTF-8',           # Кодировка
            mclass=1,                  # Класс сообщения
            mwi=0,                     # Индикатор сообщения голосовой почты
            alt_dcs=0,                 # Альтернативная схема кодирования
            rpi=0,                     # Индикатор ответа
            boxc_id='box1',            # ID бокса
        )
        print(result)
    except KannelValidationError as e:
        print(f"Ошибка валидации данных: {e}")
    except KannelConnectionError as e:
        print(f"Ошибка подключения к серверу: {e}")
    except ValueError as e:
        print(f"Ошибка в параметрах: {e}")


if __name__ == '__main__':
    send_sms('+79038805678', 'Привет, мир!')
```

## Использование в командной строке:

### Базовый пример отправки SMS:

```bash
export KANNEL_USER="ваш логин"
export KANNEL_PASS="ваш пароль"
export KANNEL_URL="http://localhost:13013/"

smsaero_kannel_send \
    --username "$KANNEL_USER" \
    --password "$KANNEL_PASS" \
    --url "$KANNEL_URL" \
    --phone +79038805678 \
    --message 'Привет, мир!' \
    --coding 0 \
    --dlr-url 'http://your-server.com/dlr' \
    --dlr-mask 31 \
    --account 'account1' \
    --debug  # опционально для включения подробного логирования
```

### Отправка SMS с DLR URL:

```bash
# Использование внешнего DLR URL
smsaero_kannel_send \
    --username "$KANNEL_USER" \
    --password "$KANNEL_PASS" \
    --url "$KANNEL_URL" \
    --phone +79038805678 \
    --message 'Привет, мир!' \
    --dlr-url "http://your-server.com:5555/dlr" \
    --dlr-mask 31
```

## Запуск в Docker:

```bash
# Базовый пример
docker pull 'smsaero/smsaero_python_kannel:latest'

docker run -it --rm smsaero/smsaero_python_kannel:latest \
    smsaero_kannel_send \
    --username "ваш логин" \
    --password "ваш пароль" \
    --url "http://localhost:13013/" \
    --phone +79038805678 \
    --message 'Hello, World!'

# Пример с пробросом порта для DLR
docker run -it -p 5555:5555 --rm smsaero/smsaero_python_kannel:latest \
    smsaero_kannel_send \
    --username "ваш логин" \
    --password "ваш пароль" \
    --url "http://kannel:13013/" \
    --phone +79038805678 \
    --message 'Hello, World!' \
    --dlr-url "http://hostname:5555/dlr"
```

### Примечания по работе с DLR в Docker:

1. При использовании локального DLR сервера:
   - Используйте `--dlr-host "0.0.0.0"` для прослушивания всех интерфейсов
   - Пробрасывайте порт с помощью `-p host_port:container_port`
   - Убедитесь, что порт не занят на хост-машине
   - Проверьте настройки файрвола

2. При использовании внешнего DLR URL:
   - URL должен быть доступен из контейнера
   - Убедитесь, что порт открыт и доступен
   - Проверьте настройки маршрутизации

3. Возможные проблемы с портами:
   - Порт может быть занят другим процессом
   - Файрвол может блокировать входящие соединения
   - Неправильная настройка проброса портов в Docker
   - Конфликт с другими сервисами

## Параметры отправки SMS

### Основные параметры:

- `phone` - Номер телефона в международном формате
- `message` - Текст сообщения (до 960 символов)
- `coding` - Кодировка сообщения:
  - `0` - GSM 7-bit (по умолчанию)
  - `1` - 8-bit
  - `8` - UCS2 (UTF-16)
- `dlr_url` - URL для получения статусов доставки
- `dlr_mask` - Маска DLR (Delivery Report):
  - `0` - Без DLR
  - `1` - Только успешная доставка
  - `2` - Только ошибки
  - `4` - Промежуточные статусы
  - `31` - Все статусы (по умолчанию)
- `account` - Опциональный идентификатор аккаунта
- `dlr_host` - Хост для локального DLR сервера (по умолчанию "0.0.0.0")
- `dlr_port` - Порт для локального DLR сервера (по умолчанию 8080)

### Дополнительные параметры Kannel:

- `priority` - Приоритет сообщения (0-3)
- `validity` - Время жизни сообщения в минутах
- `charset` - Кодировка сообщения (например, 'UTF-8')
- `mclass` - Класс сообщения (0-3)
- `mwi` - Индикатор сообщения голосовой почты (0-1)
- `alt_dcs` - Альтернативная схема кодирования
- `rpi` - Индикатор ответа
- `boxc_id` - ID бокса
- `meta_data` - Метаданные в формате 'key1=value1,key2=value2'

## Статусы сообщений

При отправке SMS могут быть получены следующие статусы:
- `accepted` - Сообщение принято (0: Accepted)
- `queued` - Сообщение поставлено в очередь (3: Queued)
- `delivered` - Сообщение доставлено
- `failed` - Ошибка доставки
- `unknown` - Неизвестный статус

## Исключения

* `KannelConnectionError` - исключение при ошибке подключения к Kannel серверу
* `ValueError` - исключение при некорректных входных данных (неверный формат телефона, URL и т.д.)

## Особенности

- Поддержка длинных сообщений (до 960 символов)
- Автоматическая валидация номера телефона
- Поддержка международного формата номеров
- Поддержка различных кодировок
- Поддержка DLR (Delivery Report) через HTTP сервер
- Автоматическое ожидание конечного статуса доставки
- Подробное логирование при необходимости
- Механизм повторных попыток при ошибках
- Поддержка всех параметров Kannel HTTP API

## Требования

- Python 3.9+
- requests
- aiohttp
- phonenumbers

## Лицензия

MIT License
