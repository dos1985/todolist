import factory

from bot.models import TgUser
from core.models import User
from goals import models
from goals.models import BoardParticipant


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@test.com")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password('password')


class BoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Board

    title = factory.Sequence(lambda n: f"Test Board {n}")


# class GoalCategoryFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = models.GoalCategory
#
#     title = factory.Sequence(lambda n: f"Test Category {n}")
#     user = factory.SubFactory(UserFactory)
#     board = factory.SubFactory(BoardFactory)
#
#     @factory.post_generation
#     def participants(self, create, extracted, **kwargs):
#         if not create:
#             return
#         if extracted:
#             for participant in extracted:
#                 BoardParticipantFactory(user=participant, board=self.board, role=BoardParticipant.Role.owner)
#         else:
#             BoardParticipantFactory(user=self.user, board=self.board, role=BoardParticipant.Role.owner)
class GoalCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GoalCategory
        skip_postgeneration_save = True

    title = factory.Sequence(lambda n: f"Test Category {n}")
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    @factory.post_generation
    def set_board_and_user(self, create, extracted, **kwargs):
        if not create:
            return
        BoardParticipant.objects.get_or_create(board=self.board, user=self.user, role=BoardParticipant.Role.owner)


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Goal

    title = factory.Sequence(lambda n: f"Test Goal {n}")
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    description = factory.Faker('text')


class GoalCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GoalComment

    text = factory.Sequence(lambda n: f"Test comment {n}")

    # Убедимся, что пользователь и цель принадлежат одному и тому же доске
    user = factory.SubFactory(UserFactory)
    # board = factory.SubFactory(BoardFactory)
    goal = factory.SubFactory(GoalFactory)



class BoardParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BoardParticipant

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)


class TgUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TgUser

    chat_id = factory.Sequence(lambda n: n)
    user_id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: f"tguser{n}")
    related_user = None
    verification_code = "testcode"