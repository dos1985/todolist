from typing import Any
from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class VerificationView(GenericAPIView):
    model = TgUser
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer: Serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        tg_user = self._get_tg_user(serializer.validated_data['verification_code'])

        tg_user.user = request.user
        tg_user.save()

        TgClient(settings.BOT_TOKEN).send_message(tg_user.chat_id, 'проверка завершена')

        return Response(TgUserSerializer(tg_user).data)

    @staticmethod
    def _get_tg_user(verification_code: str) -> TgUser:
        try:
            return TgUser.objects.get(verification_code=verification_code)
        except TgUser.DoesNotExist:
            raise NotFound('Invalid verification code')

