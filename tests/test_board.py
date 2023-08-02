import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
import json
from core.models import User
from goals import serializers
from goals.models import Board, BoardParticipant
from tests.factories import BoardFactory, BoardParticipantFactory


@pytest.mark.django_db
def test_create_board(auth_client, user):
    board = BoardFactory()
    BoardParticipantFactory(board=board, user=user)

    data = {
        "title": "Test board",
    }

    response = auth_client.post(reverse('board-create'), data)
    print(response.content)

    assert response.status_code == HTTP_201_CREATED


@pytest.mark.django_db
def test_board_list(auth_client):
    # Создаём двух пользователей
    user1 = User.objects.create_user(username='test1', password='testpassword1')
    user2 = User.objects.create_user(username='test2', password='testpassword2')

    # Аутентифицируемся под пользователем user1
    auth_client.force_authenticate(user=user1)

    # Создаём две доски и присваиваем их пользователю user1
    board1 = Board.objects.create(title='Test Board 1')
    board2 = Board.objects.create(title='Test Board 2')
    BoardParticipant.objects.create(board=board1, user=user1, role=BoardParticipant.Role.owner)
    BoardParticipant.objects.create(board=board2, user=user1, role=BoardParticipant.Role.owner)

    # Создаём дополнительную доску и присваиваем её пользователю user2
    board3 = Board.objects.create(title='Test Board 3')
    BoardParticipant.objects.create(board=board3, user=user2, role=BoardParticipant.Role.owner)

    # Выполняем GET-запрос для получения списка досок
    response = auth_client.get(reverse('board-list'))

    # Проверяем, что статус ответа 200 OK
    if response.status_code != 200:
        print(response.data)
    assert response.status_code == 200

    # Проверяем, что в ответе присутствуют доски пользователя user1 и отсутствует доска пользователя user2
    board_titles = [board['title'] for board in response.data]
    assert 'Test Board 1' in board_titles
    assert 'Test Board 2' in board_titles
    assert 'Test Board 3' not in board_titles


@pytest.mark.django_db
def test_retrieve(auth_client, board):
    response = auth_client.get(reverse('board-detail', args=[board.pk]))
    expected_response = serializers.BoardSerializer(instance=board).data
    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_delete(auth_client, board):
    response = auth_client.delete(reverse('board-detail', args=[board.pk]))

    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_update(auth_client, board):
    response = auth_client.put(reverse('board-detail', args=[board.pk]),
                               data=json.dumps({"title": "put test title", "participants": []}),
                               content_type="application/json")

    assert response.status_code == 200

    assert response.data.get('title') == "put test title"

