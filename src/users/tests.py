import base64

from unittest.mock import patch
from PIL import Image

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTests(TestCase):
    """Testea el API de usuarios (publico)"""
    payload = {
        'email': 'test@mail.com',
        'first_name': 'Bob',
        'last_name': 'Marley',
        'password': '123456',
        'cellphone': '+51999999999'
    }
    sample_photo = SimpleUploadedFile(
        'photo.png', b'file_content', content_type='image/png'
    )

    def setUp(self):
        self.client = APIClient()

        image = Image.new('RGB', (100, 100))
        image.save(self.sample_photo)
        self.sample_photo.seek(0)

        # Se convierte los bytes del archivo anterior a base64
        # ya que no se puede enviar archivos con JSON al mismo tiempo
        self.encoded_content = base64.b64encode(
            self.sample_photo.read()
        ).decode()

    @patch('django.db.models.ImageField.pre_save', return_value=True)
    def test_create_valid_user_successful(self, ps):
        """Testea que se pueda crear un usuario valido"""
        payload = self.payload.copy()
        payload['photo'] = self.encoded_content
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=res.data.get('id'))
        self.assertTrue(user.check_password(self.payload.get('password')))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Testea que no se pueda crear un usuario que ya existe"""
        create_user(**self.payload)

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testea que el pass deberia ser al menos 6 caracteres"""
        payload = self.payload.copy()
        payload['password'] = '123'

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload.get('email')
        )
        self.assertFalse(user_exists)
