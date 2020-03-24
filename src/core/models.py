from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from phonenumber_field.modelfields import PhoneNumberField

from . import utils


class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        """Crea y guarda un nuevo usuario"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password,  **extra_fields):
        """Crea y guarda un nuevo super usuario"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    cellphone = PhoneNumberField(null=True, blank=True)
    photo = models.ImageField(
        upload_to=utils.PathAndRename('Users', randomize=True),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
