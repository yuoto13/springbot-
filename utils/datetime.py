# Маппинг месяцев на русском языке
months = {
    1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
    7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
}

# Функция для форматирования даты на русском языке
def format_date(date):
    return f"{date.day} {months[date.month]}"
