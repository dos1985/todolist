from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from core.models import User
from goals.models import Goal, GoalCategory


class TgState:
    DEFAULT = 0
    CATEGORY_CHOOSE = 1
    GOALS_CREATE = 2

    def __init__(self, state, category_id=None):
        self.state = state
        self.category_id = category_id

    def set_state(self, state):
        self.state = state

    def set_category_id(self, category_id):
        self.category_id = category_id


STATE = {}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def get_state(self, chat_id):
        return STATE.get(chat_id, TgState(TgState.DEFAULT))

    def set_state(self, chat_id, state):
        STATE[chat_id] = state

    def choose_category(self, msg, tg_user):
        goal_categories = GoalCategory.objects.filter(
            board__participants__user=tg_user.related_user,
            is_deleted=False,
        )

        goal_category_str = '\n'.join(['- ' + goal.title for goal in goal_categories])

        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Ваши активные категории: \n {goal_category_str} \n Выберите категорию:'
        )

        self.set_state(msg.chat.id, TgState(TgState.CATEGORY_CHOOSE))

    def get_goals(self, msg: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.related_user, status=True)
        if goals.exists():
            goal_str = '\n'.join(['- ' + goal.title for goal in goals])
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Ваши активные цели: \n {goal_str}'
            )
        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text='У вас нет активных целей.'
            )

    def get_cancel(self, msg: Message):
        self.set_state(msg.chat.id, TgState(TgState.DEFAULT))
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Операция отменена',
        )

    def check_category(self, msg: Message):
        category = GoalCategory.objects.filter(
            title=msg.text
        ).first()
        if category:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Введите заголовок цели'
            )

            tg_user, _ = TgUser.objects.get_or_create(
                user_id=msg.msg_from.id,
                chat_id=msg.chat.id,
            )

            tg_user.selected_category = category
            tg_user.save()

            self.set_state(
                msg.chat.id,
                TgState(TgState.GOALS_CREATE, category_id=category.id)
            )
        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Категории "{msg.text}" не существует'
            )

    def create_goal(self, msg, tg_user):
        text = msg.text.strip()

        if not tg_user.related_user:
            reply_text = "Вы не связаны с пользователем. Пожалуйста, выполните /start, чтобы связаться."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        if ' ' not in text:  # проверяем наличие пробела в тексте
            reply_text = "Вы не указали заголовок цели. Пожалуйста, используйте формат '/create [заголовок цели]'."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        title = text.split(' ', 1)[1]

        category = GoalCategory.objects.filter(id=self.get_state(msg.chat.id).category_id).first()
        if not category:
            reply_text = "Вы не выбрали категорию. Пожалуйста, используйте /categories, чтобы выбрать категорию."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        try:
            goal = Goal.objects.create(
                title=title,
                user=tg_user.related_user,
                category=category,
                description="Default description",
            )
            reply_text = f"Цель \"{goal.title}\" успешно создана в категории \"{category.title}\"."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
        except ValidationError as e:
            reply_text = "Ошибка при создании цели. Пожалуйста, убедитесь, что вы выбрали категорию и ввели название."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

    # def check_verification(self, tg_user, msg):
    #     if not tg_user.related_user:
    #         code = tg_user.set_verification_code()
    #         self.tg_client.send_message(chat_id=msg.chat.id,
    #                                     text=f"Верифицируйте свой аккаунт. Код верификации: {code}")
    #         return False  # пользователь не верифицирован
    #     return True  # пользователь верифицирован

    def handle_message(self, msg):
        tg_user, created = TgUser.objects.get_or_create(
            user_id=msg.msg_from.id,
            chat_id=msg.chat.id,
        )

        if created:
            code = tg_user.set_verification_code()
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Добро пожаловать в бот @todolistmarlenbot!\nДля продолжения работы необходимо привязать\nВаш аккаунт на сайте vmr-group.kz {code}'
            )
            return

        if msg.text: # Проверяем, есть ли текст в сообщении
            if tg_user.verification_code and tg_user.verification_code in msg.text:
                tg_user.verify_user(tg_user.verification_code)
                self.tg_client.send_message(
                    chat_id=msg.chat.id,
                    text='Ваш аккаунт успешно верифицирован.'
                )
                return

        if not tg_user.related_user:
            code = tg_user.set_verification_code()
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Пожалуйста, верифицируйте ваш аккаунт. Ваш код верификации: {code}'
            )
            return

        if '/start' == msg.text:
            if not tg_user.related_user:
                code = tg_user.set_verification_code()
                reply_text = f"Связь с пользователем установлена. Ваш код верификации: {code}"
            else:
                reply_text = "Вы уже связаны с пользователем."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        print("Related User:", tg_user.related_user)

        current_state = self.get_state(msg.chat.id)

        if '/goals' == msg.text:
            self.get_goals(msg, tg_user)

        elif '/create' == msg.text:
            self.choose_category(msg, tg_user)

        elif '/cancel' == msg.text:
            self.get_cancel(msg)

        elif current_state.state == TgState.CATEGORY_CHOOSE:
            self.check_category(msg)

        elif current_state.state == TgState.GOALS_CREATE:
            self.create_goal(msg, tg_user)

        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Неизвестная команда {msg.text}'
            )

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                if item.message:  # Проверка на None
                    self.handle_message(item.message)
                else:
                    print(f"Получено обновление без сообщения: {item}")
