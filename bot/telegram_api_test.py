import requests

def get_updates_example(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    print(response.json())

# Замените "YOUR_TOKEN" на ваш реальный токен
get_updates_example("6366561845:AAEyn4xEkTJ3FhSSaaitS1AFmfvzsWDEAj8")
