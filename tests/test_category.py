import json
import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from goals import serializers
from goals.models import GoalCategory, Board, BoardParticipant
from tests.factories import BoardParticipantFactory, GoalCategoryFactory


@pytest.mark.django_db
def test_create_category(auth_client, user, board):
    data = {
        "title": "Test Board",
        "board": board.id,
    }
    response = auth_client.post(reverse('goalcategory-create'), data)
    assert response.status_code == HTTP_201_CREATED

    # Проверяем, что в базе данных действительно создан новый объект с указанными данными
    category_exists = GoalCategory.objects.filter(title="Test Board", board=board).exists()

    assert category_exists, "Category was not created in the database"


@pytest.mark.django_db
def test_list_goal_categories_with_permission(auth_client, user, board):
    # Создаём пользователя и доску
    BoardParticipantFactory()

    # Создаем категорию целей и связываем с доской
    GoalCategoryFactory(title="Category 1", board=board, user=user)
    GoalCategoryFactory(title="Category 2", board=board, user=user)

    # Выполняем GET-запрос для получения списка категорий
    response = auth_client.get(reverse('goalcategory-list'))

    # Проверяем, что статус ответа 200 OK
    assert response.status_code == 200

    # Проверяем, что в ответе присутствуют категории пользователя
    category_titles = [category['title'] for category in response.data]
    assert 'Category 1' in category_titles
    assert 'Category 2' in category_titles


@pytest.mark.django_db
def test_retrieve(auth_client, user, board):
    # Создаем доску, которую будем связывать с категорией
    board = Board.objects.create(title='Test Board')
    BoardParticipant.objects.create(board=board, user=user, role=BoardParticipant.Role.owner)
    # Создаем категорию целей и связываем ее с доской
    goal_category = GoalCategoryFactory(title="Test Category", board=board, user=user)
    response = auth_client.get(reverse('goalcategory-detail', args=[goal_category.pk]))
    expected_response = serializers.GoalCategorySerializer(instance=goal_category).data

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_update(auth_client, board, user, goal_category):
    response = auth_client.put(
        reverse('goalcategory-detail', kwargs={'pk': goal_category.pk}),
        data=json.dumps({
            "title": "put test title", "participants": []
        }),
        content_type="application/json")

    assert response.status_code == 200
    assert response.data.get('title') == "put test title"


@pytest.mark.django_db
def test_delete(auth_client, board, goal_category):
    response = auth_client.delete(reverse('goalcategory-detail', args=[goal_category.pk]))

    assert response.status_code == HTTP_204_NO_CONTENT