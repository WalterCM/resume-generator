from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core import models


CREATE_SKILL_URL = reverse('skills:create')
LIST_SKILLS_URL = reverse('skills:list')


def create_skill(name):
    models.Skill.objects.create_skill(name=name)


class PublicTests(TestCase):
    """Testea el API de habilidades (publico)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_skill_unauthorized(self):
        """Testea que autenticacion sea requerida para crear una habilidad"""
        res = self.client.post(CREATE_SKILL_URL, {})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_skills_unauthorized(self):
        """Testea que autenticacion sea requerida para listar habilidaes"""
        res = self.client.get(LIST_SKILLS_URL)

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

    def test_non_admin_create_skill_fail(self):
        """Testea que un no administrador no pueda crear un skill"""
        user = get_user_model().objects.create_user(
            email='test@test.com',
            password='123456'
        )
        self.client.force_authenticate(user=user)

        res = self.client.post(CREATE_SKILL_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_skills_successful(self):
        """Testea que se puedan listar las habilidades creadas"""
        skills = ['C++', 'Python', 'Java', 'HTML']
        for skill in skills:
            create_skill(skill)

        res = self.client.get(LIST_SKILLS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0].get('name'), skills[0])
        self.assertEqual(res.data[1].get('name'), skills[3])
        self.assertEqual(res.data[2].get('name'), skills[2])
        self.assertEqual(res.data[3].get('name'), skills[1])
