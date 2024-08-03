# Weather Forecast Bot

Этот бот отслеживает погоду в указанном городе и отправляет обновления в Telegram.

## Настройка

### Шаг 1: Клонирование репозитория

Клонируйте репозиторий:

```sh
git clone https://your-repo-url.git
cd your-repo-directory
```

### Шаг 2: Создание конфигурационного файла

Создайте файл `test_config.py` на основе шаблона `test_config_template.py` и заполните его своими данными:

```sh
cp test_config_template.py test_config.py
```

Отредактируйте `test_config.py`, добавив свои данные:

```python
# test_config.py

BOT_TOKEN = 'your_telegram_bot_token_here'
WEATHER_API_KEY = 'your_openweathermap_api_key_here'
```

### Шаг 3: Установка зависимостей

Установите зависимости из файла `requirements.txt`:

```sh
pip install -r requirements.txt
```

### Шаг 4: Запуск бота

Запустите бота:

```sh
python main.py
```

## Зависимости

Для работы бота необходимы следующие зависимости:

- `aiogram`: для взаимодействия с Telegram.
- `aiohttp`: для выполнения асинхронных HTTP-запросов.
- `geopy`: для работы с геолокацией.

Все зависимости указаны в файле `requirements.txt` и могут быть установлены с помощью команды:

```sh
pip install -r requirements.txt
```