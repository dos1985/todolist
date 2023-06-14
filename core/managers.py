from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _



class UserRoles(models.TextChoices):
    USER = 'USR', _('user')
    ADMIN = 'ADM', _("admin")


class UserManager(BaseUserManager):
    """Функция создания пользователя — в нее мы передаем обязательные поля"""

    def create_user(self, email, first_name, last_name, phone, role=UserRoles.USER, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
        )
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, first_name, last_name, phone, role=UserRoles.ADMIN, password=None):
        """Функция для создания суперпользователя — с ее помощью мы создаем админинстратора
        это можно сделать с помощью команды createsuperuser"""

        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            role=role,
        )

        user.save(using=self._db)
        return user
