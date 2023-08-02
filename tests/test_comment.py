import json
import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from goals import serializers
from goals.models import BoardParticipant, GoalComment
from tests.factories import BoardFactory, BoardParticipantFactory, GoalCommentFactory


@pytest.mark.django_db
def test_create_comment(auth_client, goal, goal_comment):
    data = {
        "text": "Test Comment",
        "goal": goal.id,
    }
    response = auth_client.post(reverse('goalcomment-create'), data)
    assert response.status_code == HTTP_201_CREATED

    # Проверяем, что в базе данных действительно создан новый объект с указанными данными
    comments_exists = GoalComment.objects.filter(text="Test Comment", goal=goal).exists()

    assert comments_exists, "Category was not created in the database"


@pytest.mark.django_db
def test_list_comments(auth_client, user, board, goal_category, goal):
    board = BoardFactory(title='Test Board')
    BoardParticipantFactory(board=board, user=user, role=BoardParticipant.Role.owner)

    GoalCommentFactory(text="Comment 1", goal=goal, user=user)
    GoalCommentFactory(text="Comment 2", goal=goal, user=user)

    response = auth_client.get(reverse('goalcomment-list'))

    assert response.status_code == HTTP_200_OK

    comment_texts = [comment['text'] for comment in response.data]
    assert 'Comment 1' in comment_texts
    assert 'Comment 2' in comment_texts


@pytest.mark.django_db
def test_retrieve_comment(auth_client, goal_comment, goal, user):
    # Создаем комментарий
    goal_comment = GoalCommentFactory(text="test text", user=user, goal=goal)
    response = auth_client.get(reverse('goalcomment-detail', args=[goal_comment.pk]))
    expected_response = serializers.GoalCommentSerializer(instance=goal_comment).data

    assert response.status_code == HTTP_200_OK
    assert response.data == expected_response


@pytest.mark.django_db
def test_update_comment(auth_client, user, goal, goal_comment):
    # Создаем комментарий
    goal_comment = GoalCommentFactory(text="test text", user=user, goal=goal)
    response = auth_client.put(
        reverse('goalcomment-detail', kwargs={'pk': goal_comment.pk}),
        data=json.dumps({
            "text": "Updated test comment",
            "goal": goal.pk,
            "user": user.pk,
        }),
        content_type="application/json"
    )

    assert response.data.get('text') == "Updated test comment"


@pytest.mark.django_db
def test_delete_comment(auth_client, user, goal_comment, goal):
    #pdb.set_trace()
    # Создаем комментарий
    goal_comment = GoalCommentFactory(text="test text", user=user, goal=goal)
    # Убеждаемся, что комментарий существует
    assert GoalComment.objects.filter(pk=goal_comment.pk).first()
    response = auth_client.delete(reverse('goalcomment-detail', args=[goal_comment.pk]))
    assert response.status_code == HTTP_204_NO_CONTENT
    # Убеждаемся, что комментарий был удален
    assert not GoalComment.objects.filter(pk=goal_comment.pk).exists()
