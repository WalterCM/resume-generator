from rest_framework import generics

from users import serializers


class CreateUserView(generics.CreateAPIView):
    """Crea un nuevo usuario en el sistema"""
    serializer_class = serializers.UserSerializer
