from django.urls import path

from .views import GoalCategoryCreateView, GoalCategoryView, GoalCreateView, GoalListView,\
    GoalCommentCreateView, GoalCommentListView, GoalCommentView, BoardCreateView, \
    GoalCategoryListView, BoardListAPIView, BoardView, GoalView

urlpatterns = [
    path("goals/goal_category/create", GoalCategoryCreateView.as_view(), name='goalcategory-create'),
    path("goals/goal_category/list", GoalCategoryListView.as_view(), name='goalcategory-list'),
    path("goals/goal_category/<int:pk>", GoalCategoryView.as_view(), name='goalcategory-detail'),
    path("goals/goal/create", GoalCreateView.as_view(), name='goal-create'),
    path("goals/goal/list", GoalListView.as_view(), name='goal-list'),
    path("goals/goal/<int:pk>", GoalView.as_view(), name='goal-detail'),
    path("goals/goal_comment/create", GoalCommentCreateView.as_view(), name='goalcomment-create'),
    path("goals/goal_comment/list", GoalCommentListView.as_view(), name='goalcomment-list'),
    path("goals/goal_comment/<int:pk>", GoalCommentView.as_view(), name='goalcomment-detail'),
    path("goals/board/create", BoardCreateView.as_view(), name='board-create'),
    path("goals/board/list", BoardListAPIView.as_view(), name='board-list'),
    path("goals/board/<int:pk>", BoardView.as_view(), name='board-detail'),



]