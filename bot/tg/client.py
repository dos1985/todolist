import requests

from bot.tg import schemas

class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 0) -> schemas.GetUpdatesResponse:
        url = self.get_url('getUpdates')
        response = requests.post(url, data={'offset': offset, 'timeout': timeout}) # Используем метод POST и передаем параметры в теле запроса
        return schemas.GET_UPDATES_SCHEMA.load(response.json())

    def send_message(self, chat_id: int, text: str) -> schemas.SendMessageResponse:
        url = self.get_url("sendMessage")
        response = requests.post(url, data={"chat_id": chat_id, "text": text}) # Используем метод POST и передаем параметры в теле запроса
        return schemas.SEND_MESSAGE_RESPONSE_SCHEMA.load(response.json())
