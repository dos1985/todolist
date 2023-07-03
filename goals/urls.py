from django.urls import path

from .views import GoalCategoryCreateView, GoalCategoryListView, GoalCategoryView, GoalCreateView, GoalListView, \
    GoalView, GoalDetailView, GoalCommentCreateView, GoalCommentListView, GoalCommentView


urlpatterns = [
    path("goals/goal_category/create", GoalCategoryCreateView.as_view()),
    path("goals/goal_category/list", GoalCategoryListView.as_view()),
    path("goals/goal_category/<pk>", GoalCategoryView.as_view()),
    path("goals/goal/create", GoalCreateView.as_view()),
    path("goals/goal/list", GoalListView.as_view()),
    path("goals/goal/<pk>", GoalDetailView.as_view()),
    path("goals/goal_comment/create", GoalCommentCreateView.as_view()),
    path("goals/goal_comment/list", GoalCommentListView.as_view()),
    path("goals/goal_comment/<pk>", GoalCommentView.as_view()),


]