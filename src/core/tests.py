from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError


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
