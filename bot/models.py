import random
import string

from django.db import models
from core.models import User

# Генерируемое случайное слово для verification_code
CODE_VOCABULARY = string.ascii_letters + string.digits


class TgUser(models.Model):
    """ Модель для хранения данных пользователей Telegram """
    chat_id = models.BigIntegerField(verbose_name='Чат ID', default=0)   # Уникальный идентификатор чата в Telegram
    user_id = models.BigIntegerField(verbose_name="User ID", unique=True, default=0)     # Уникальный идентификатор пользователя в Telegram
    username = models.CharField(max_length=512, verbose_name="Username", null=True, blank=True) # Имя пользователя в Telegram (опционально)
    related_user = models.ForeignKey(User, models.PROTECT, null=True, blank=True, verbose_name='Связанный пользователь') # Связанный пользователь (если есть) из модели User
    verification_code = models.CharField(max_length=32, verbose_name="Код подтверждения", null=True, blank=True) # Код подтверждения

    def set_verification_code(self) -> str:
        """Метод для установки нового кода подтверждения"""
        code = "".join([random.choice(CODE_VOCABULARY) for _ in range(12)])
        self.verification_code = code

        # Убедимся, что связанный пользователь сохраняется правильно после верификации
        if self.related_user:
            self.save()
        else:
            # Если связанного пользователя нет, то создаем и сохраняем его здесь
            # Замените 'User' на вашу модель пользователя, которая связывается с TgUser
            user = User.objects.create(username=f"Telegram_User_{self.user_id}")
            self.related_user = user
            self.save()

        return code  # Возвращаем сгенерированный код

    def __str__(self):
        return f'Telegram User: {self.user_id}'

    class Meta:
        verbose_name = "Телеграм Пользователь"
        verbose_name_plural = "Телеграм Пользователи"


# class TgUser(models.Model):
#     telegram_chat_id = models.CharField(max_length=100)
#     telegram_user_id = models.CharField(max_length=100)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#
#     def __str__(self):
#         return f"Telegram User ID: {self.telegram_user_id}"

