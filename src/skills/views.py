from rest_framework import generics
from rest_framework import permissions

from skills import serializers


class CreateSkillView(generics.CreateAPIView):
    """Crea un nuevo usuario en el sistema"""
    serializer_class = serializers.SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)
