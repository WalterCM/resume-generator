from django.contrib.auth import get_user_model

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    photo = Base64ImageField()

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'password', 'first_name',
            'last_name', 'photo', 'cellphone'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'min_length': 6}
        }

    def create(self, validated_data):
        """Crea un nuevo usuario y lo retorna"""
        return get_user_model().objects.create_user(**validated_data)
