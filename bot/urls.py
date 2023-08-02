from django.urls import path

from .views import VerificationView

urlpatterns = [
    path('bot/verify', VerificationView.as_view(), name='bot-verification'),
]