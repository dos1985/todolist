import random
import string
from django.db import models
from core.models import User
from goals.models import DatesModelMixin

# Генерируемое случайное слово для verification_code
CODE_VOCABULARY = string.ascii_letters + string.digits


class TgUser(DatesModelMixin):
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
        self.save()
        return code

    def verify_user(self, verification_code):
        """Метод для проверки и обновления статуса верификации пользователя."""
        if verification_code == self.verification_code:
            self.verification_code = None
            self.save()
            return True
        return False

    def __str__(self):
        return f'Telegram User: {self.user_id}'

    class Meta:
        verbose_name = "Телеграм Пользователь"
        verbose_name_plural = "Телеграм Пользователи"




