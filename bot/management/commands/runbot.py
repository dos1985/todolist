from datetime import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand


from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
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


STATE = TgState(state=TgState.DEFAULT)



class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def choose_category(self, msg, tg_user):
        # Получаем все доступные категории для пользователя
        goal_categories = GoalCategory.objects.filter(
            board__participants__user=tg_user.related_user,
            is_deleted=False,
        )

        # Строим строку с категориями
        goal_category_str = '\n'.join(['- ' + goal.title for goal in goal_categories])

        # Отправляем сообщение
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Ваши активные категории: \n {goal_category_str} \n Выберите категорию:'
        )

        # Сохраняем состояние
        STATE.set_state(TgState.CATEGORY_CHOOSE)

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
        STATE.set_state(TgState.DEFAULT)
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
                text=f'Ведите заголовок цели'
            )

            # Получаем объект tg_user для этого сообщения
            tg_user, _ = TgUser.objects.get_or_create(
                user_id=msg.msg_from.id,
                chat_id=msg.chat.id,
            )

            # Устанавливаем выбранную категорию
            tg_user.selected_category = category
            tg_user.save()

            STATE.set_category_id(category.id)
            STATE.set_state(TgState.GOALS_CREATE)
        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Категории "{msg.text}" не существует'
            )

    def create_goal(self, msg, tg_user):
        # Получаем текст из сообщения
        text = msg.text.strip()

        # Проверяем, что у пользователя есть связанный пользователь
        if not tg_user.related_user:
            reply_text = "Вы не связаны с пользователем. Пожалуйста, выполните /start, чтобы связаться."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        # Разбиваем текст на части по пробелам и извлекаем название цели
        title = text.split(' ', 1)[1]

        # Проверяем, что у пользователя есть выбранная категория
        category = GoalCategory.objects.filter(id=STATE.category_id).first()
        if not category:
            reply_text = "Вы не выбрали категорию. Пожалуйста, используйте /categories, чтобы выбрать категорию."
            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        # Создаем новую цель
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

    def handle_message(self, msg):
        tg_user, created = TgUser.objects.get_or_create(
            user_id=msg.msg_from.id,
            chat_id=msg.chat.id,
        )
        if created:
            tg_user.set_verification_code()
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text='''Добро пожаловать в бот @todolistmarlenbot!\n
                Для продолжения работы необходимо привязать
                Ваш аккаунт на сайте vmr-group.kz'''
            )
            code = tg_user.set_verification_code()
            self.tg_client.send_message(tg_user.chat_id, f'верификационный код: {code}')

        if '/start' == msg.text:
            # Проверяем, что у пользователя есть связанный пользователь
            if not tg_user.related_user:
                # Если связи нет, пытаемся установить ее
                code = tg_user.set_verification_code()
                reply_text = f"Связь с пользователем установлена. Ваш код верификации: {code}"
            else:
                # Если связь уже установлена, просто сообщаем об этом
                reply_text = "Вы уже связаны с пользователем."

            self.tg_client.send_message(chat_id=msg.chat.id, text=reply_text)
            return

        print("Related User:", tg_user.related_user)

        if '/goals' == msg.text:
            self.get_goals(msg, tg_user)

        elif '/create' == msg.text:
            self.choose_category(msg, tg_user)

        elif '/cancel' == msg.text:
            self.get_cancel(msg)

        elif STATE.state == TgState.CATEGORY_CHOOSE:
            self.check_category(msg)

        elif STATE.state == TgState.GOALS_CREATE:
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
                print(item.message)
                if hasattr(item, 'message'):
                    self.handle_message(item.message)
