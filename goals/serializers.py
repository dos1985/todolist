from django.db import transaction
from rest_framework import serializers

from core.models import User
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from core.serializers import UserSerializer


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания категории цели."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def create(self, validated_data):
        """Создаем категорию цели и назначаем ее текущему пользователю."""
        user = validated_data.pop("user")
        category = GoalCategory.objects.create(user=user, **validated_data)
        return category

    def validate(self, attrs):
        """Проверка: текущий пользователь должен быть владельцем доски."""
        user = self.context['request'].user
        is_owner = BoardParticipant.objects.filter(
            user=user,
            board=attrs['board'],
            role=BoardParticipant.Role.owner
        ).exists()

        if not is_owner:
            raise serializers.ValidationError("You are not owner of this board")
        return attrs


class GoalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания целей."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

    def validate_category(self, value):
        """Валидация: проверка что пользователь является владельцем или автором доски."""
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted category")
        if not BoardParticipant.objects.filter(
                user=self.context["request"].user,
                board=value.board,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise serializers.ValidationError("not owner or writer of board")
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для представления категории цели."""
    user = UserSerializer(read_only=True)
    board = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalSerializer(serializers.ModelSerializer):
    """Сериализатор для представления цели."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", 'title', 'description')


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментариев к цели."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


class GoalCommentSerializer(serializers.ModelSerializer):
    """Сериализатор для представления комментария к цели."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class BoardCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания доски."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated")
        fields = "__all__"

    def create(self, validated_data):
        """Создаем доску и добавляем текущего пользователя в качестве владельца."""
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        board.participants.create(user=user, role=BoardParticipant.Role.owner)
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    """Сериализатор для представления участника доски."""
    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.Role.choices
    )
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор для представления доски."""
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = "__all__"
        read_only_fields = ("id", "created", "updated")


    def update(self, instance, validated_data):
        """Обновляем информацию доски и участников."""
        owner = validated_data.pop("user")
        new_participants = validated_data.pop("participants")
        new_by_id = {part["user"].id: part for part in new_participants}

        old_participants = instance.participants.exclude(user=owner)
        print("Old participants before processing: ", old_participants)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if (
                            old_participant.role
                            != new_by_id[old_participant.user_id]["role"]
                    ):
                        old_participant.role = new_by_id[old_participant.user_id][
                            "role"
                        ]
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    board=instance, user=new_part["user"], role=new_part["role"]
                )

            instance.title = validated_data["title"]
            instance.save()

        return instance



class BoardListSerializer(serializers.ModelSerializer):
    """Сериализатор для представления списка досок."""
    class Meta:
        model = Board
        fields = "__all__"
        # fields = ['id', 'created', 'updated', 'title', 'is_deleted']



