from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


CARD_TITLE_MAX_LENGTH = 50


class DemoUserManager(BaseUserManager):
    def create_user(self, user_id, display_name, password=None):
        if not user_id:
            raise ValueError("missing user_id")
        if not display_name:
            raise ValueError("missing display_name")
        user = self.model(user_id=user_id, display_name=display_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, display_name, password):
        user = self.create_user(user_id, display_name, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class DemoUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20)
    display_name = models.CharField(max_length=30)

    objects = DemoUserManager()

    USERNAME_FIELD = "user_id"

    def get_short_name(self):
        return self.display_name

    def get_full_name(self):
        return self.display_name


class Card(models.Model):
    pass
