from unittest.mock import patch

from django.test import TestCase
from django.test import Client

from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db.utils import OperationalError

from django.urls import reverse

from rest_framework import status

from . import models


class UserModelTests(TestCase):
    payload = {
        'email': 'test@mail.com',
        'password': '123456',
        'first_name': 'Bob',
        'last_name': 'Marley',
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


class SkillModelTests(TestCase):
    payload = {
        'name': 'C++'
    }

    def test_create_skill_successful(self):
        """Testea la funcion de modelo, create_skill"""
        skill = models.Skill.objects.create_skill(**self.payload)

        self.assertEqual(skill.name, self.payload.get('name'))

    def test_create_skill_no_name(self):
        """Testea que falle si se intenta crear un skill sin nombre"""
        with self.assertRaises(ValueError):
            models.Skill.objects.create_skill()

    def test_user_add_skill(self):
        user = get_user_model().objects.create_user(
            email='test@mail.com',
            password='123456'
        )
        proficiency = 80
        skill = models.Skill.objects.create_skill(**self.payload)
        user_skill = user.add_skill(skill, proficiency)

        self.assertTrue(user.skills.filter().exists())
        self.assertEqual(user_skill.user, user)
        self.assertEqual(user_skill.skill, skill)
        self.assertEqual(user_skill.proficiency, proficiency)


class JobExperienceModelTests(TestCase):
    payload = {
        'title': 'Administrador',
        'company': 'ADP',
        'start_date': '2019-09-02',
        'end_date': '2019-12-24'
    }

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@mail.com',
            password='123456'
        )

    def test_add_job_succesful(self):
        """Testea la funcion de modelo, create_job"""
        job = self.user.add_job(**self.payload)

        self.assertEqual(job.title, self.payload.get('title'))
        self.assertEqual(job.company, self.payload.get('company'))

    def test_create_job_no_title(self):
        """Testea que se pueda crear un trabajo sin titulo"""
        payload = self.payload.copy()
        del payload['title']

        job = self.user.add_job(**payload)

        self.assertEqual(job.company, payload.get('company'))

    def test_create_job_no_company_fail(self):
        """Testea que no se pueda crear un trabajo sin company"""
        payload = self.payload.copy()
        del payload['company']

        with self.assertRaises(ValueError):
            self.user.add_job(**payload)

    def test_create_job_no_start_date_fail(self):
        """Testea que se pueda crear un trabajo sin start_date"""
        payload = self.payload.copy()
        del payload['start_date']

        with self.assertRaises(ValueError):
            self.user.add_job(**payload)

    def test_create_job_no_end_date_fail(self):
        """Testea que se pueda crear un trabajo sin end_date"""
        payload = self.payload.copy()
        del payload['end_date']

        with self.assertRaises(ValueError):
            self.user.add_job(**payload)

    def test_create_job_to_present_day(self):
        """Testea que presente pueda ser fecha final"""
        payload = self.payload.copy()
        del payload['end_date']
        payload['present_day'] = True

        job = self.user.add_job(**payload)

        self.assertEqual(job.title, self.payload.get('title'))
        self.assertEqual(job.company, self.payload.get('company'))

    def test_create_job_end_date_before_start_date_fail(self):
        """Testea que no se pueda crear un trabajo con el end_date antes"""
        payload = self.payload.copy()
        payload['start_date'] = '2020-09-02'

        with self.assertRaises(ValidationError):
            self.user.add_job(**payload)


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


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Testea esperar a la base de datos cuando esta disponible"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Testea esperar a la base de datos"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
