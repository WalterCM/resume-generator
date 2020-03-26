from rest_framework import serializers

from core import models


class SkillSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Skill"""

    class Meta:
        model = models.Skill
        fields = (
            'id', 'name'
        )
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        """Crea un nuevo usuario y lo retorna"""
        return self.Meta.model.objects.create_skill(**validated_data)
