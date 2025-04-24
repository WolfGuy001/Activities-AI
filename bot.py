import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
import requests


TOKEN = '7475097618:AAGzzSlfRelwn4C5qr2y6zHtefVZOzBRMPo'


logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я готов помочь тебе с поиском спортивных организации по твоим предпочтениям', parse_mode = 'HTML')
    await message.answer('Для начала, ответь на несколько вопросов:', parse_mode='HTML')

@dp.message()
async def filter_messages(message: Message):
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
                "content": "You are a helpful assistant"
            },
            {
                "role": "user",
                "content": message.text
            }
        ],
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    # pprint(data)

    text = data['choices'][0]['message']['content']
    bot_text = text.split('</think>\n\n')[1]

    await message.answer(bot_text, parse_mode = "Markdown")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())