from django.db import models
from django.utils import timezone

from core.models import User

# class DatesModelMixin(models.Model):
#     class Meta:
#         abstract = True  # Помечаем класс как абстрактный – для него не будет таблички в БД
#
#     created = models.DateTimeField(verbose_name='Дата создания', default=timezone.now)
#     updated = models.DateTimeField(verbose_name='Дата последнего обновления', default=timezone.now)


class GoalCategory(models.Model):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)
    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    def save(self, *args, **kwargs):
        if not self.id:  # Когда объект только создается, у него еще нет id
            self.created = timezone.now()  # проставляем дату создания
        self.updated = timezone.now()  # проставляем дату обновления
        return super().save(*args, **kwargs)


class Goal(models.Model):
    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"


    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критически"

    title = models.CharField(verbose_name='Название', max_length=255, default=None)
    user = models.ForeignKey('core.User', verbose_name='Автор', related_name='goals', on_delete=models.PROTECT, default=None)
    description = models.TextField(verbose_name='Описание', default=None)
    category = models.ForeignKey(GoalCategory, verbose_name='Категория', on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', choices=Priority.choices,
                                                default=Priority.medium)
    due_date = models.DateTimeField(verbose_name='Дата дедлайна', null=True, blank=True, default=None)

    def __str__(self):
        return self.title


class GoalComment(models.Model):
    class Meta:
        verbose_name = 'Комментарий к цели'
        verbose_name_plural = 'Комментарии к цели'

    user = models.ForeignKey('core.User', verbose_name='Автор', related_name='goal_comment', on_delete=models.PROTECT)
    goal = models.ForeignKey(Goal, verbose_name='Цель', related_name='goal_comment', on_delete=models.PROTECT)
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)
