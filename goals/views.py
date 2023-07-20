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
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
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
        return GoalCategory.objects.filter(Q(user=user) | Q(board__participants__user=user), is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermission]

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
    model = Goal
    permission_classes = [permissions.IsAuthenticated] #GoalCategoryPermission,  GoalPermission
    serializer_class = GoalCreateSerializer

    # def perform_create(self, serializer):
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=self.request.user)


class GoalListView(ListAPIView):
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
    ordering_fields = ['due_date', 'priority']
    ordering = ['priority', 'due_date']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermission]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Удаление всех связанных комментариев
            GoalComment.objects.filter(goal=instance).delete()
            # Помечаем цель как удаленную
            instance.is_deleted = True
            instance.save()



class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
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
        return GoalComment.objects.filter(goal__user=self.request.user)

class GoalCommentView(RetrieveUpdateDestroyAPIView):
    serializer_class = GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(goal__user=self.request.user)


class BoardCreateView(CreateAPIView):
    model = Board
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class BoardListAPIView(ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "created"]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(participants__user=user, is_deleted=False)



class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
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


