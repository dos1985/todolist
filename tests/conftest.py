from rest_framework.test import APIClient
from core.models import User
from goals.models import BoardParticipant


import pytest
from tests.factories import (
    UserFactory,
    BoardFactory,
    GoalCategoryFactory,
    GoalFactory,
    GoalCommentFactory,
    BoardParticipantFactory,
)

@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def user(db):
    return UserFactory(username='test')

@pytest.fixture
def board(db, auth_client):
    board = BoardFactory()
    user = User.objects.get(username='test')
    BoardParticipant.objects.create(board=board, user=user, role=BoardParticipant.Role.owner)
    return board

@pytest.fixture
def goal_category(db, user, board):
    return GoalCategoryFactory(title="Test Category", user=user, board=board)

@pytest.fixture
def goal(db, user, goal_category):
    return GoalFactory(title="Test Goal", user=user, category=goal_category)


@pytest.fixture
def goal_comment(db):
    return GoalCommentFactory()

@pytest.fixture
def board_participant(db):
    return BoardParticipantFactory()