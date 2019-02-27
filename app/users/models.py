from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class User(AbstractUser):
    first_name = None
    last_name = None
    username_validator = ASCIIUsernameValidator

    # This is just an example to append a new field TODO: remove it
    age = models.SmallIntegerField(null=True)
    # follower = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
