from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
import asyncio
import time
import requests

TOKEN = "7475097618:AAGzzSlfRelwn4C5qr2y6zHtefVZOzBRMPo"

bot = Bot(TOKEN)
dp = Dispatcher()

# Переменные для хранения ответов
user_city = None
user_age = None
user_preferences = None


# Состояния бота
class UserState:
    ASK_CITY = 1
    ASK_AGE = 2
    ASK_PREFERENCES = 3


current_state = {}


@dp.message(Command("start"))
async def start_cmd(message: Message):
    chat_id = message.chat.id
    current_state[chat_id] = UserState.ASK_CITY
    time.sleep(1)
    await message.answer('Из какого ты города?', parse_mode = 'HTML')


@dp.message()
async def handle_message(message: Message):
    chat_id = message.chat.id
    global user_city, user_age, user_preferences

    if chat_id not in current_state:
        current_state[chat_id] = None

    if current_state[chat_id] == UserState.ASK_CITY:
        user_city = message.text
        current_state[chat_id] = UserState.ASK_AGE
        time.sleep(1)
        await message.answer(f"Принято, город {user_city}\n"
                             f"\n"
                             f"Сколько тебе лет?", parse_mode = 'HTML')

    elif current_state[chat_id] == UserState.ASK_AGE:
        user_age = message.text
        current_state[chat_id] = UserState.ASK_PREFERENCES
        time.sleep(1)
        await message.answer(f'Отлично!\n'
                             f'\n'
                             f'Теперь напиши "в двух словах":\n'
                             f"Какое именно место ты ищешь?\n"
                             f"Чем планируешь заниматься?\n"
                             f"Чего хочешь достичь?", parse_mode = 'HTML')

    elif current_state[chat_id] == UserState.ASK_PREFERENCES:
        user_preferences = message.text
        time.sleep(1)
        await message.answer(f"Спасибо за ответы!")
        time.sleep(1)
        await message.answer(f"Генерирую для тебя список организаций\n"
                             f"Нужно немного подожать", parse_mode = 'HTML')

        current_state[chat_id] = None

        print(f"User data: {user_city}, {user_age}, {user_preferences}")

        url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQ5NDVlZmJjLTFkMzYtNGI2MC1hMTc5LTFiZDczYmNhMmU3ZCIsImV4cCI6NDg5OTA3MzAzNX0.C2HYOd4JxMVHKzRi0_Lyy3pNkW0V8yXqq5s5tdAe86Lml6Z6QZkOQXT-n6Qpn5Ul8F1rfAYkou2Q2Va-JzjvAQ",
        }

        data = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - профссиональный ассистент по подбору спортивных организаций для человека по запросам, которые к тебе приходят"
                },
                {
                    "role": "user",
                    "content":f'Пришел запрос от пользователя: Город - {user_city}, Возраст - {user_age}, Предпочтения - {user_preferences}. Найди на сайте 2gis.ru организации, которые подходят пользователю. Выведи их списком'
                }
            ],
        }

        response = requests.post(url, headers=headers, json=data)
        data = response.json()
        # pprint(data)

        text = data['choices'][0]['message']['content']
        bot_text = text.split('</think>\n\n')[1]

        await message.answer(bot_text, parse_mode="Markdown")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())