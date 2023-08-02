from django.contrib.auth import login, logout
from rest_framework import generics, status, permissions
from rest_framework.generics import RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer, USER_MODEL, \
    UpdatePasswordSerializer


class RegisterView(generics.CreateAPIView):
    """RegisterView используется для обработки регистрации пользователей. Поддерживает только HTTP POST запросы."""
    serializer_class = RegistrationSerializer


class UserLoginView(generics.GenericAPIView):
    """ UserLoginView используется для обработки входа пользователей. Поддерживает только HTTP POST запросы."""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)
        return Response(serializer.data)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """ProfileView используется для получения, обновления или удаления профиля пользователя.
    Поддерживает HTTP GET, PUT, PATCH и DELETE запросы."""
    serializer_class = ProfileSerializer
    queryset = USER_MODEL.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(UpdateAPIView):
    """UpdatePasswordView используется для обновления пароля пользователя. Поддерживает HTTP PUT и PATCH запросы."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        """Переопределяем стандартный метод get_object, чтобы всегда возвращать текущего пользователя."""
        return self.request.user