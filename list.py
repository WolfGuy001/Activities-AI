import requests
from pprint import pprint


url = "https://api.intelligence.io.solutions/api/v1/models"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjQ5NDVlZmJjLTFkMzYtNGI2MC1hMTc5LTFiZDczYmNhMmU3ZCIsImV4cCI6NDg5OTA3MzAzNX0.C2HYOd4JxMVHKzRi0_Lyy3pNkW0V8yXqq5s5tdAe86Lml6Z6QZkOQXT-n6Qpn5Ul8F1rfAYkou2Q2Va-JzjvAQ",
}

response = requests.get(url, headers=headers)
data = response.json()


for i in range(len(data['data'])):
    name = data['data'][i]['id']
    print(name)

