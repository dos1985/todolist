from rest_framework import serializers

from bot.models import TgUser
from rest_framework.exceptions import ValidationError


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.IntegerField(source='chat_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TgUser
        fields = ('tg_id', 'username', 'verification_code', 'user_id')
        read_only_fields = ('tg_id', 'username', 'user_id')

    def validate_verification_code(self, code: str) -> str:
        try:
            self.tg_user = TgUser.objects.get(verification_code=code)
        except TgUser.DoesNotExist:
            raise ValidationError('Field is incorrect')
        return code

    def update(self, instance: TgUser, validated_data: dict):
        return self.tg_user