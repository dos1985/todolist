from django.urls import path

from .views import GoalCategoryCreateView, GoalCategoryView, GoalCreateView, GoalListView,\
    GoalCommentCreateView, GoalCommentListView, GoalCommentView, BoardCreateView, \
    GoalCategoryListView, BoardListAPIView, BoardView, GoalView

urlpatterns = [
    path("goals/goal_category/create", GoalCategoryCreateView.as_view()),
    path("goals/goal_category/list", GoalCategoryListView.as_view()),
    path("goals/goal_category/<int:pk>", GoalCategoryView.as_view()),
    path("goals/goal/create", GoalCreateView.as_view()),
    path("goals/goal/list", GoalListView.as_view()),
    path("goals/goal/<int:pk>", GoalView.as_view()),
    path("goals/goal_comment/create", GoalCommentCreateView.as_view()),
    path("goals/goal_comment/list", GoalCommentListView.as_view()),
    path("goals/goal_comment/<int:pk>", GoalCommentView.as_view()),
    path("goals/board/create", BoardCreateView.as_view()),
    path("goals/board/list", BoardListAPIView.as_view()),
    path("goals/board/<int:pk>", BoardView.as_view()),



]