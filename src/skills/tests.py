from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_SKILL_URL = reverse('skills:create')


class PublicTests(TestCase):
    """Testea el API de habilidades (publico)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_skill_unauthorized(self):
        """Testea que autenticacion sea requerida para crear una habilidad"""
        res = self.client.post(CREATE_SKILL_URL, {})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateTests(TestCase):
    """Testea el API de habilidades (privado)"""
    payload = {
        'name': 'C++'
    }

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='123456'
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_skill_successfull(self):
        """Testea la creacion de habilidades hechas por admins"""
        res = self.client.post(CREATE_SKILL_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
