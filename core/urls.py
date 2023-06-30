from django.urls import path

from .views import RegisterView, UserLoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path('core/signup', RegisterView.as_view()),
    path('core/login', UserLoginView.as_view()),
    path('core/profile', ProfileView.as_view()),
    path('core/update_password', UpdatePasswordView.as_view()),

]

