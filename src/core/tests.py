from unittest.mock import patch

from django.test import TestCase
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
# from django.core.exceptions import ValidationError
from rest_framework import status


class UserModelTests(TestCase):
    payload = {
        'email': 'test@mail.com',
        'password': '123456',
        'cellphone': '+51999999999',
        'photo': SimpleUploadedFile(
            'photo.png', b'file_content', content_type='image/png'
        )
    }

    @patch('django.db.models.ImageField.pre_save', return_value=True)
    def test_create_user_with_email_successful(self, ps):
        """Testea que se pueda crear un nuevo usuario con email """
        user = get_user_model().objects.create_user(**self.payload)

        self.assertEqual(user.email, self.payload.get('email'))
        self.assertTrue(user.check_password(self.payload.get('password')))
        self.assertEqual(user.cellphone, self.payload.get('cellphone'))

    @patch('django.db.models.ImageField.pre_save', return_value=True)
    def test_create_user_email_normalized(self, ps):
        """Testea que se pueda crear un usuario con el email normalizado"""
        payload = self.payload.copy()
        payload['email'] = 'test@MAIL.COM'

        user = get_user_model().objects.create_user(**payload)

        self.assertEqual(user.email, payload.get('email').lower())

    def test_create_user_no_email(self):
        """Testea que crear un usuario sin email mande un error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123456')

    def test_create_new_superuser(self):
        """Testea que se pueda crear un nuevo super usuario"""
        user = get_user_model().objects.create_superuser(**self.payload)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class AdminSiteTests(TestCase):
    payload = {
        'email': 'test@mail.com',
        'password': '123456',
        'cellphone': '+51999999999',
        'photo': SimpleUploadedFile(
            'photo.png', b'file_content', content_type='image/png'
        )
    }

    @patch('django.db.models.ImageField.pre_save', return_value=True)
    def setUp(self, ps):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='123456'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            **self.payload
        )

    def test_users_listed(self):
        """Testea que los usuarios sean listados en la pagina de usuarios"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.display_name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Testea que se puedan editar usuarios"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        """Testea que se puedan crear usuarios"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
