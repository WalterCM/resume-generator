from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
# from django.core.exceptions import ValidationError


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
