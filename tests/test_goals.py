import json
import pytest
from django.urls import reverse
from rest_framework import serializers
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_200_OK
from goals.models import Goal, GoalCategory, Board, BoardParticipant
from tests.factories import GoalFactory
from goals import serializers


@pytest.mark.django_db
def test_create_goals(auth_client, user, board, goal_category):

    data = {
        "title": "Test Goal",
        "description": "Test description",
        "board": board.id,
        "category": goal_category.id,
    }
    response = auth_client.post(reverse('goal-create'), data)

    assert response.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_get_goal_list(auth_client, user, board, goal_category):
    board = Board.objects.create(title='test board')
    BoardParticipant.objects.create(user=user, board=board)

    # Затем создайте несколько целей
    GoalFactory(title="Goal 1", description="Description 1", user=user, category=goal_category)
    GoalFactory.create(title="Goal 2", description="Description 2", user=user, category=goal_category)

    # Выполняем GET-запрос для получения списка целей
    response = auth_client.get(reverse('goal-list'))

    # Проверяем, что статус ответа 200 OK
    assert response.status_code == 200

    # Проверяем, что в ответе присутствуют созданные цели
    goal_titles = [goal['title'] for goal in response.data]
    assert 'Goal 1' in goal_titles
    assert 'Goal 2' in goal_titles


@pytest.mark.django_db
def test_retrieve_goal(auth_client, user, goal_category, goal):  # Создаем цели

    response = auth_client.get(reverse('goal-detail', args=[goal.pk]))
    expected_response = serializers.GoalSerializer(instance=goal).data

    assert response.status_code == HTTP_200_OK
    assert response.data == expected_response


@pytest.mark.django_db
def test_update(auth_client, user, goal_category, goal):   # Создание цели

    # Обновление цели
    response = auth_client.put(
        reverse('goal-detail', kwargs={'pk': goal.pk}),
        data=json.dumps({
            # "title": "put test title",
            "status": Goal.Status.done,
            "priority": Goal.Priority.high,
            "category": goal_category.id
        }),
        content_type="application/json"
    )

    assert response.status_code == 200
    # assert response.data.get('title') == "put test title"
    assert response.data.get('status') == Goal.Status.done
    assert response.data.get('priority') == Goal.Priority.high


@pytest.mark.django_db
def test_delete(auth_client, user, goal_category, goal):    # Создание цели с указанием необходимых полей
    # Проверяем, есть ли объект в базе данных перед удалением
    goal = Goal.objects.filter(pk=goal.pk).first()
    assert goal is not None, "Goal does not exist"

    response = auth_client.delete(reverse('goal-detail', args=[goal.pk]))

    assert response.status_code == HTTP_204_NO_CONTENT


