from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from phonenumber_field.modelfields import PhoneNumberField

from . import utils


class UserManager(BaseUserManager):

    def create_user(self, email=None, password=None, first_name='',
                    last_name='', **extra_fields):
        """Crea y guarda un nuevo usuario"""
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password,  **extra_fields):
        """Crea y guarda un nuevo super usuario"""
        user = self.create_user(
            email=email,
            password=password,
            first_name='',
            last_name=''
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    cellphone = PhoneNumberField(blank=True)
    photo = models.ImageField(
        upload_to=utils.PathAndRename('Users', randomize=True),
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    skills = models.ManyToManyField(
        'Skill',
        related_name='skills',
        through='UserSkill'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def display_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def add_skill(self, skill=None, proficiency=None):
        if not skill:
            raise ValueError('You need to pass a skill as argument')
        if not proficiency:
            raise ValueError('Proficiency is required')

        user_skill = UserSkill(
            user=self,
            skill=skill,
            proficiency=proficiency
        )

        user_skill.save()

        return user_skill

    def add_job(self, title='', company=None, start_date=None,
                end_date=None, present_day=False):
        if not company:
            raise ValueError('Job requires company')
        if not start_date:
            raise ValueError('Job requires a start date')
        if not present_day:
            if not end_date:
                raise ValueError('Job requires an end date')

            if end_date < start_date:
                raise ValidationError('Start date should be before end date')

        job = Job(
            title=title,
            company=company,
            start_date=start_date,
            end_date=end_date,
            present_day=present_day,
            user=self
        )

        job.save()

        return job


class SkillManager(models.Manager):

    def create_skill(self, name=None):
        """Crea y guarda una habilidad"""
        if not name:
            raise ValueError('Skill requires a name')

        skill = self.model(name=name)
        skill.save()

        return skill


class Skill(models.Model):
    name = models.CharField(unique=True, max_length=255)

    objects = SkillManager()

    class Meta:
        ordering = ['name']


class UserSkill(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    proficiency = models.SmallIntegerField()


class Job(models.Model):
    title = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    present_day = models.BooleanField(default=False)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
