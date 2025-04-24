import telebot
import random
from telebot import types
import time
import requests
import json

# Замени 'YOUR_BOT_TOKEN' на токен своего бота
BOT_TOKEN = '7475097618:AAGzzSlfRelwn4C5qr2y6zHtefVZOzBRMPo'
bot = telebot.TeleBot(BOT_TOKEN)

url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQ5NDVlZmJjLTFkMzYtNGI2MC1hMTc5LTFiZDczYmNhMmU3ZCIsImV4cCI6NDg5OTA3MzAzNX0.C2HYOd4JxMVHKzRi0_Lyy3pNkW0V8yXqq5s5tdAe86Lml6Z6QZkOQXT-n6Qpn5Ul8F1rfAYkou2Q2Va-JzjvAQ",
}

users_file = 'users.json'
user_states = {}
search_queries = {}
events_channel_link = 'ССЫЛКА_НА_ВАШ_ТЕЛЕГРАМ_КАНАЛ' # Замените на реальную ссылку
workout_program_requests = {}

def load_users():
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def generate_unique_id(users):
    while True:
        user_id = random.randint(100, 999)
        if str(user_id) not in users:
            return user_id

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users = load_users()
    if str(chat_id) in users:
        bot.send_message(chat_id, "😊 Вы уже зарегистрированы!")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('🏋️ Создать программу тренировок')
        markup.row('📅 Ближайшие события', '🗺️ Поиск мест')
        markup.row('🏆 Рейтинг', '👤 Профиль')
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(chat_id,"👋 Привет! Этот бот - твой личный компаньон в спорте и ведении здорового образа жизни\n"
                                " \n"
                                "С нами ты сможешь:\n"
                                "- Быть в курсе спортивных событий\n"
                                "- Выбрать и записаться на секцию\n"
                                "- Написать программу тренировок\n"
                                "- Оценивать свой прогресс\n"
                                "- Соревноваться с другими пользователями...\n"
                                "И многое другое!)\n"
                                " \n"
                                "Но сначала, давай пройдем простую регистрацию")
        user_states[chat_id] = {'state': 'waiting_for_real_name'}
        time.sleep(5)
        bot.send_message(chat_id, "Пожалуйста, введи свое реальное имя:\n"
                          "_Его не увидит никто кроме тебя_", parse_mode="Markdown")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_real_name')
def get_real_name(message):
    chat_id = message.chat.id
    user_states[chat_id]['real_name'] = message.text
    user_states[chat_id]['state'] = 'waiting_for_nickname'
    bot.send_message(chat_id, "📝 Отлично! Теперь введи свой никнейм:\n"
                              "_Его будут видеть другие в топе_", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🏋️ Создать программу тренировок')
def ask_for_workout_details(message):
    chat_id = message.chat.id
    workout_program_requests[chat_id] = {'state': 'waiting_for_details'}
    bot.send_message(chat_id, "Отлично! Расскажите, какую программу тренировок вы хотите составить (например, опишите свою цель, предпочтения, уровень подготовки и прочее, как можно подробнее):")

@bot.message_handler(func=lambda message: workout_program_requests.get(message.chat.id, {}).get('state') == 'waiting_for_details')
def get_workout_details(message):
    chat_id = message.chat.id
    details = message.text
    workout_program_requests[chat_id]['details'] = details

    bot.send_message(chat_id, f"✅ Запрос принят!\n"
                              f"Нужно немножко подождать 😉")

    print(workout_program_requests)

    data = {
        "model": "microsoft/Phi-3.5-mini-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Ты профссиональный личный тренер"
            },
            {
                "role": "user",
                "content": f'Придумай программу тренировок по такому запросу:{workout_program_requests}. Не расписывай все слишком подробно, просто коротко напиши программу тренировок.'
            }
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    text = data['choices'][0]['message']['content']
    print(text)
    bot.send_message(chat_id, text, parse_mode="Markdown")
    bot.send_message(chat_id, 'Ваша программа составлена!\n'
                              'Сохраните в заметках чтобы не потерять', parse_mode="Markdown")

    del workout_program_requests[chat_id]  # Очищаем запрос

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_nickname')
def get_nickname(message):
    chat_id = message.chat.id
    user_states[chat_id]['nickname'] = message.text
    user_states[chat_id]['state'] = 'waiting_for_age'
    bot.send_message(chat_id, "🔢 Какой у тебя возраст?:\n"
                              "_Нужно для подбора секций_", parse_mode="Markdown")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_age' and message.text.isdigit())
def get_age(message):
    chat_id = message.chat.id
    user_states[chat_id]['age'] = int(message.text)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Мужской', 'Женский', 'Нетакуся')
    user_states[chat_id]['state'] = 'waiting_for_gender'
    bot.send_message(chat_id, "🧍 Выбери свой пол:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_age' and not message.text.isdigit())
def invalid_age(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⚠️ Пожалуйста, введите возраст цифрами.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_gender' and message.text in ['Мужской', 'Женский', 'Нетакуся'])
def get_gender(message):
    chat_id = message.chat.id
    user_states[chat_id]['gender'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Сургут', 'Ханты-мансийск', 'Нижневартовск', 'Нефтеюганск', 'Когалым', 'Нягань')
    user_states[chat_id]['state'] = 'waiting_for_city'
    bot.send_message(chat_id, "🏙️ Выберите ваш город:", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_gender' and message.text not in ['Мужской', 'Женский'])
def invalid_gender(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⚠️ Пожалуйста, выберите пол из предложенных кнопок.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_city' and message.text in ['Сургут', 'Ханты-мансийск', 'Нижневартовск', 'Нефтеюганск', 'Когалым', 'Нягань'])
def get_city(message):
    chat_id = message.chat.id
    user_states[chat_id]['city'] = message.text
    users = load_users()
    user_id = generate_unique_id(users)
    users[str(chat_id)] = {
        'id': user_id,
        'real_name': user_states[chat_id]['real_name'],
        'nickname': user_states[chat_id]['nickname'],
        'age': user_states[chat_id]['age'],
        'gender': user_states[chat_id]['gender'],
        'city': user_states[chat_id]['city'],
        'rating': 0
    }
    save_users(users)
    del user_states[chat_id]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('📅 Ближайшие события', '🗺️ Поиск мест')
    markup.row('🏆 Рейтинг', '👤 Профиль')
    bot.send_message(chat_id, "✅ Регистрация окончена!", reply_markup=markup)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id, {}).get('state') == 'waiting_for_city' and message.text not in ['Сургут', 'Ханты-мансийск', 'Нижневартовск', 'Нефтеюганск', 'Когалым', 'Нягань'])
def invalid_city(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "⚠️ Пожалуйста, выберите город из предложенных кнопок.")

@bot.message_handler(func=lambda message: message.text == '📅 Ближайшие события')
def send_events_link(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"📢 Канал с событиями: "
                              f"\n{events_channel_link}")

@bot.message_handler(func=lambda message: message.text == '🗺️ Поиск мест')
def ask_for_search_query(message):
    chat_id = message.chat.id
    search_queries[chat_id] = {'state': 'waiting_for_query'}
    bot.send_message(chat_id, "🤔 Кратко опиши, какое место ты хочешь найти(например спортзал или секция по боксу)?\n"
                              "\n"
                              "Мы составим список из нескольких мест которые подходят вам больше всего")

@bot.message_handler(func=lambda message: search_queries.get(message.chat.id, {}).get('state') == 'waiting_for_query')
def get_search_query(message):
    chat_id = message.chat.id
    query = message.text
    search_queries[chat_id]['query'] = query
    del search_queries[chat_id]
    # Здесь можно было бы реализовать логику поиска мест,
    # но в данном примере мы просто записываем запрос.
    bot.send_message(chat_id, f"✅ Запрос принят!\n"
                              f"Нужно немножко подождать 😉")
    with open('organizations.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(data)

    data = {
        "model": "microsoft/Phi-3.5-mini-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Ты профссиональный личный тренер"
            },
            {
                "role": "user",
                "content": f'''Составь список ТОЛЬКО из данных списка {data} по запросу: {search_queries}. 
            Формат ответа для каждого места:
            1. [Название] - [Краткое описание на основе названия, 2-3 слова]
            ...
            Не добавляй контакты, ссылки или другие поля из файла. Используй только перечисленные в файле названия.'''
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    text = data['choices'][0]['message']['content']
    print(text)
    bot.send_message(chat_id, text, parse_mode="Markdown")

    del search_queries[chat_id]

@bot.message_handler(func=lambda message: message.text == '🏆 Рейтинг')
def show_rating(message):
    chat_id = message.chat.id
    users = load_users()
    if not users:
        bot.send_message(chat_id, "😥 Пока нет зарегистрированных пользователей.")
        return
    sorted_users = sorted(users.items(), key=lambda item: item[1]['rating'], reverse=True)
    rating_text = ("🏆 Топ-3:\n"
                   "\n")
    for i, (user_id, user_data) in enumerate(sorted_users):
        medal = ''
        if i == 0:
            medal = '🥇 '
        elif i == 1:
            medal = '🥈 '
        elif i == 2:
            medal = '🥉 '
        rating_text += f"{medal}{user_data['nickname']} - Рейтинг: {user_data['rating']}\n"
        if i == 2: # Показываем только топ 3 с медалями
            break
    # Добавляем остальных пользователей без медалей
    if len(sorted_users) > 3:
        rating_text += "\n\nДругие пользователи:\n\n"
        for i, (user_id, user_data) in enumerate(sorted_users[3:]):
            rating_text += f"{user_data['nickname']} - {user_data['rating']}\n"

    bot.send_message(chat_id, rating_text)

@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def show_profile(message):
    chat_id = message.chat.id
    users = load_users()
    if str(chat_id) in users:
        user_data = users[str(chat_id)]
        profile_text = (
            "👤 Ваш профиль:\n"
            f"🆔 ID: {user_data['id']}\n"
            f"⭐ Рейтинг: {user_data['rating']}\n"
            f"Имя: {user_data['real_name']}\n"
            f"Ник: {user_data['nickname']}\n"
            f"Возраст: {user_data['age']}\n"
            f"🏙️ Город: {user_data['city']}"
        )
        markup = types.InlineKeyboardMarkup()
        delete_button = types.InlineKeyboardButton("🗑️ Удалить профиль", callback_data=f'delete_profile_{chat_id}')
        markup.add(delete_button)
        bot.send_message(chat_id, profile_text, reply_markup=markup)
    else:
        bot.send_message(chat_id, "⚠️ Ваш профиль не найден. Пожалуйста, зарегистрируйтесь с помощью команды /start.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_profile_'))
def delete_profile(call):
    chat_id_to_delete = str(call.data.split('_')[-1])
    users = load_users()
    if chat_id_to_delete in users:
        del users[chat_id_to_delete]
        save_users(users)
        bot.send_message(call.message.chat.id, "🗑️ Ваш профиль успешно удален.")
    else:
        bot.send_message(call.message.chat.id, "⚠️ Произошла ошибка при удалении профиля.")
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)