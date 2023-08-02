import django_filters
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter, GoalCategoryFilter
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from goals.permissions import BoardPermissions, GoalCategoryPermission, GoalPermission
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalSerializer, \
    GoalCategoryCreateSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, \
    BoardSerializer, BoardListSerializer


class GoalCategoryCreateView(CreateAPIView):
    """Представление для создания категории цели.
    Предоставляет POST метод для создания новой категории цели.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """Представление для просмотра списка категорий целей.
    Поддерживает GET запросы для просмотра всех категорий целей.
    """
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermission]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = ['board']
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        user = self.request.user
        return GoalCategory.objects.filter(
            board__participants__user=user
        ).exclude(is_deleted=True).distinct()


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления категории цели.
    Поддерживает GET, PUT, PATCH и DELETE запросы для работы с категорией цели.
    """
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermission]

    # def get_queryset(self):
    #     user = self.request.user
    #     return GoalCategory.objects.filter(Q(user=user) | Q(board__participants__user=user), is_deleted=False)

    def get_queryset(self):
        user = self.request.user
        return GoalCategory.objects.filter(Q(user=user) | Q(board__participants__user=user), is_deleted=False)

    def perform_destroy(self, instance):
        # Переводим все цели данной категории в статус "Архив"
        Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        # Помечаем категорию как удаленную
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    """Представление для создания цели.
    Поддерживает POST запросы для создания новой цели.
    """
    permission_classes = [permissions.IsAuthenticated] #GoalCategoryPermission,  GoalPermission
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    """Представление для просмотра списка целей.
    Поддерживает GET запросы для просмотра всех целей.
    """
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_class = GoalDateFilter
    ordering_fields = ['due_date']
    ordering = ['due_date']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user
        board_ids = BoardParticipant.objects.filter(user=user).values_list('board_id', flat=True)
        return Goal.objects.filter(category__board_id__in=board_ids).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления цели.
    Поддерживает GET, PUT, PATCH и DELETE запросы для работы с целью.
    """
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermission]

    def get_queryset(self):
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Удаление всех связанных комментариев
            GoalComment.objects.filter(goal=instance).delete()
            # Помечаем цель как удаленную
            instance.is_deleted = True
            instance.save()


class GoalCommentCreateView(CreateAPIView):
    """Представление для создания комментария к цели.
    Поддерживает POST запросы для создания нового комментария к цели.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    """Представление для просмотра списка комментариев к цели.
    Поддерживает GET запросы для просмотра всех комментариев к цели.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления комментария к цели.
    Поддерживает GET, PUT, PATCH и DELETE запросы для работы с комментарием к цели.
    """
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(goal__user=self.request.user)


class BoardCreateView(CreateAPIView):
    """Представление для создания доски.
    Поддерживает POST запросы для создания новой доски.
    """
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class BoardListAPIView(ListAPIView):
    """Представление для просмотра списка досок.
    Поддерживает GET запросы для просмотра всех досок.
    """
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "created"]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(participants__user=user, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления доски.
    Поддерживает GET, PUT, PATCH и DELETE запросы для работы с доской.
    """
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Board.objects.filter(participants__user_id=user_id, is_deleted=False)

    def perform_destroy(self, instance: Board):
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


