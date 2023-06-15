from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager, UserRoles



class User(AbstractUser):
    pass
    # email = models.EmailField(unique=True)
    # username = models.CharField(max_length=50)
    # phone = PhoneNumberField(max_length=20)
    # role = models.CharField(choices=UserRoles.choices, default=UserRoles.USER, max_length=10)
    #
    #
    # @property
    # def is_superuser(self):
    #     return self.is_admin
    #
    # @property
    # def is_staff(self):
    #     return self.is_admin
    #
    # def has_perm(self, perm, obj=None):
    #     return self.is_admin
    #
    # def has_module_perms(self, app_label):
    #     return self.is_admin
    #
    # # эта константа определяет поле для логина пользователя
    # USERNAME_FIELD = 'email'
    #
    # # эта константа содержит список с полями,
    # # которые необходимо заполнить при создании пользователя
    # REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone', 'role']
    #
    # # для корректной работы нам также необходимо
    # # переопределить менеджер модели пользователя
    # objects = UserManager()
    #
    # @property
    # def is_admin(self):
    #     return self.role == UserRoles.ADMIN
    #
    # @property
    # def is_user(self):
    #     return self.role == UserRoles.USER
    #
