from rest_framework import generics
from rest_framework import permissions

from skills import serializers

from core import models


class CreateSkillView(generics.CreateAPIView):
    """Crea una nueva habilidad o en el sistema"""
    serializer_class = serializers.SkillSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    )


class ListSkillsView(generics.ListAPIView):
    """Lista las habidades creadas"""
    serializer_class = serializers.SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = models.Skill.objects.all()

        return queryset
