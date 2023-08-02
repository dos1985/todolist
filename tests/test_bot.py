from unittest.mock import patch

import pytest
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from rest_framework import status
from bot.models import TgUser
from .factories import TgUserFactory, UserFactory



@pytest.mark.django_db
def test_patch_verification_view_already_related(auth_client, user):
    TgUserFactory(related_user=user, verification_code='testcode')
    response = auth_client.patch(reverse('bot-verification'), data={'verification_code': 'testcode'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['error'] == 'Вы уже связаны.'

#
# @pytest.mark.django_db
# def test_patch_verification_view_success(auth_client, user):
#
#     response = auth_client.patch(reverse('bot-verification'), data={'verification_code': 'testcode'})
#     assert response.status_code == status.HTTP_200_OK
#     auth_client.refresh_from_db()
#     assert auth_client.related_user == user
#     assert response.json() == {'tg_id': auth_client.chat_id, 'username': user.username, 'verification_code': None, 'user_id': user.id}