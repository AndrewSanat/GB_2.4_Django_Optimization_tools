from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

import pytz
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver


class ShopUser(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatars', blank=True)
    age = models.PositiveIntegerField(verbose_name = 'возраст', default=18)

    activation_key = models.CharField(max_length=128, blank=True)
    activation_key_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def is_activation_key_expired(self):
        if datetime.now(pytz.timezone(settings.TIME_ZONE)) < (self.activation_key_created + timedelta(hours=48)):
            return False
        return True


class ShopUserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'W'
    GENDER_CHOICES = (
        (MALE, 'М'),
        (FEMALE, 'Ж'),
    )
    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, unique=True, db_index=True)
    tagline = models.CharField(max_length=150, blank=True, verbose_name='тэги')
    about_me = models.TextField(blank=True, verbose_name='о себе')
    gender = models.CharField(choices=GENDER_CHOICES, blank=True, max_length=1, verbose_name='пол')

    @receiver(post_save, sender=ShopUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            ShopUserProfile.objects.create(user=instance)

    @receiver(post_save, sender=ShopUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.shopuserprofile.save()
