import requests
from pprint import pprint

url = "https://api.intelligence.io.solutions/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQ5NDVlZmJjLTFkMzYtNGI2MC1hMTc5LTFiZDczYmNhMmU3ZCIsImV4cCI6NDg5OTA3MzAzNX0.C2HYOd4JxMVHKzRi0_Lyy3pNkW0V8yXqq5s5tdAe86Lml6Z6QZkOQXT-n6Qpn5Ul8F1rfAYkou2Q2Va-JzjvAQ",
}

data = {
    "model": "microsoft/Phi-3.5-mini-instruct",
    "messages": [
        {
            "role": "system",
            "content": "Ты - профссиональный ассистент по подбору спортивных организаций для человека по запросам, которые к тебе приходят. Найди на сайте 2gis.ru организации, которые подходят пользователю. Твоим ответом должен быть словарь в таком формате: название1: (порядковый номер, координаты на карте, номер для связи и официальный сайт (если есть), ссылка на страницу в 2gis), ..."
        },
        {
            "role": "user",
            "content":f'Пришел запрос от пользователя: Город - Сургут, Возраст - 16, Предпочтения - Секция по единоборствам'
        }
    ],
}


response = requests.post(url, headers=headers, json=data)
data = response.json()
# pprint(data)

text = data['choices'][0]['message']['content']
print(text)