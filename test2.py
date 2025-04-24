import json
import os
import random
import telebot
from telebot import types

# Инициализация бота
bot = telebot.TeleBot("7475097618:AAGzzSlfRelwn4C5qr2y6zHtefVZOzBRMPo")  # Замените на свой токен

# Путь к файлу с пользователями
USERS_FILE = "users.json"

# Список доступных городов
CITIES = ["Сургут", "Ханты-Мансийск", "Нижневартовск", "Нефтеюганск", "Когалым", "Нягань"]


# Загрузка пользователей из файла
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


# Сохранение пользователей в файл
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


# Генерация уникального 4-значного ID
def generate_unique_id(users):
    while True:
        user_id = random.randint(1000, 9999)  # Случайный ID от 1000 до 9999
        if not any(user.get("user_id") == user_id for user in users.values()):
            return user_id

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Ближайшие события")
    markup.add("Поиск мест *AI*")
    markup.add("Рейтинг")
    markup.add("Профиль")
    bot.send_message(chat_id, "Главное меню:", reply_markup=markup)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    chat_id = str(message.chat.id)

    if chat_id in users:
        bot.send_message(message.chat.id, "С возвращением!")
        show_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Добро пожаловать! Давайте начнем регистрацию.")
        bot.send_message(message.chat.id, "Введите ваше реальное имя:")
        bot.register_next_step_handler(message, process_name_step)


# Процесс регистрации: шаг имени
def process_name_step(message):
    chat_id = str(message.chat.id)
    users = load_users()

    user_data = {
        "name": message.text,
        "chat_id": chat_id
    }
    users[chat_id] = user_data
    save_users(users)

    bot.send_message(message.chat.id, "Теперь введите ваш никнейм:")
    bot.register_next_step_handler(message, process_nickname_step)


# Процесс регистрации: шаг никнейма
def process_nickname_step(message):
    chat_id = str(message.chat.id)
    users = load_users()

    users[chat_id]["nickname"] = message.text
    save_users(users)

    bot.send_message(message.chat.id, "Введите ваш возраст:")
    bot.register_next_step_handler(message, process_age_step)


# Процесс регистрации: шаг возраста
def process_age_step(message):
    chat_id = str(message.chat.id)
    users = load_users()

    try:
        age = int(message.text)
        if age <= 0 or age > 120:
            raise ValueError
        users[chat_id]["age"] = age
        save_users(users)

        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Мужской", "Женский")
        bot.send_message(message.chat.id, "Выберите ваш пол:", reply_markup=markup)
        bot.register_next_step_handler(message, process_gender_step)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный возраст (число от 1 до 120):")
        bot.register_next_step_handler(message, process_age_step)


# Процесс регистрации: шаг пола
def process_gender_step(message):
    chat_id = str(message.chat.id)
    users = load_users()

    if message.text not in ["Мужской", "Женский"]:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("Мужской", "Женский")
        bot.send_message(message.chat.id, "Пожалуйста, выберите пол из предложенных вариантов:", reply_markup=markup)
        bot.register_next_step_handler(message, process_gender_step)
        return

    users[chat_id]["gender"] = message.text
    save_users(users)

    # Создаем клавиатуру с городами
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for city in CITIES:
        markup.add(city)

    bot.send_message(message.chat.id, "Выберите ваш город из списка:", reply_markup=markup)
    bot.register_next_step_handler(message, process_city_step)


# Процесс регистрации: шаг города
def process_city_step(message):
    chat_id = str(message.chat.id)
    users = load_users()

    if message.text not in CITIES:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for city in CITIES:
            markup.add(city)
        bot.send_message(message.chat.id, "Пожалуйста, выберите город из списка:", reply_markup=markup)
        bot.register_next_step_handler(message, process_city_step)
        return

    users[chat_id]["city"] = message.text
    users[chat_id]["user_id"] = generate_unique_id(users)
    users[chat_id]["rating"] = 0  # Начальный рейтинг
    save_users(users)

    bot.send_message(message.chat.id, "✅ Регистрация завершена!", reply_markup=types.ReplyKeyboardRemove())
    show_profile(message, users[chat_id])
    show_main_menu(message.chat.id)


# Показать профиль пользователя (теперь с ID)
def show_profile(message, user_data):
    profile_text = (
        f"🏆 Рейтинг: {user_data.get('rating', 0)}\n"
        f"🆔 ID: {user_data.get('user_id', 'Не указан')}\n"
        f"👤 Имя: {user_data.get('name', 'Не указано')}\n"
        f"🔹 Ник: {user_data.get('nickname', 'Не указан')}\n"
        f"📅 Возраст: {user_data.get('age', 'Не указан')}\n"
        f"🚻 Пол: {user_data.get('gender', 'Не указан')}\n"
        f"🏙️ Город: {user_data.get('city', 'Не указан')}"
    )
    bot.send_message(message.chat.id, profile_text)


# Обработчик команды /delete
@bot.message_handler(commands=['delete'])
def handle_text(message):
    users = load_users()
    chat_id = str(message.chat.id)

    if chat_id not in users:
        bot.send_message(message.chat.id, "Сначала зарегистрируйтесь с помощью /start")
        return

    if message.text == "Ближайшие события":
        bot.send_message(message.chat.id, "Подписывайтесь на наш канал с событиями: https://t.me/your_channel")

    elif message.text == "Поиск мест *AI*":
        bot.send_message(message.chat.id, "Чем вы хотите заняться? (например: кафе, кино, спорт)")
        bot.register_next_step_handler(message, process_ai_search)

    elif message.text == "Рейтинг":
        show_local_rating(message)

    elif message.text == "Профиль":
        show_profile(message, users[chat_id])


# Обработчик поиска мест через AI
def process_ai_search(message):
    # Здесь можно добавить логику обработки запроса
    # Пока просто сохраняем запрос
    user_activity = message.text
    bot.send_message(message.chat.id,
                     f"Ищем места для: {user_activity}\n(Это демо-версия, реальный поиск можно подключить позже)")
    show_main_menu(message.chat.id)


# Показать локальный рейтинг
def show_local_rating(message):
    users = load_users()
    chat_id = str(message.chat.id)

    if chat_id not in users:
        return

    user_city = users[chat_id]["city"]
    local_users = [u for u in users.values() if u.get("city") == user_city]

    # Сортируем по рейтингу (по убыванию)
    sorted_users = sorted(local_users, key=lambda x: x.get("rating", 0), reverse=True)

    if not sorted_users:
        bot.send_message(message.chat.id, "В вашем городе пока нет других пользователей")
        return

    rating_text = f"🏆 Рейтинг пользователей в {user_city}:\n\n"
    for idx, user in enumerate(sorted_users, 1):
        rating_text += f"{idx}. {user.get('nickname', 'Без ника')} - {user.get('rating', 0)} очков\n"

    bot.send_message(message.chat.id, rating_text)

def delete_profile(message):
    chat_id = str(message.chat.id)
    users = load_users()

    if chat_id not in users:
        bot.send_message(message.chat.id, "Вы еще не зарегистрированы!")
        return

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Да", "Нет")
    bot.send_message(message.chat.id, "Вы уверены, что хотите удалить свой профиль? Это действие нельзя отменить.",
                     reply_markup=markup)
    bot.register_next_step_handler(message, confirm_delete)


# Подтверждение удаления
def confirm_delete(message):
    chat_id = str(message.chat.id)
    users = load_users()

    if message.text.lower() == "да":
        del users[chat_id]
        save_users(users)
        bot.send_message(message.chat.id, "Ваш профиль был успешно удален.", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Удаление профиля отменено.", reply_markup=types.ReplyKeyboardRemove())


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()