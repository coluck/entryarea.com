from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = None
    last_name = None

    # This is just an example to append a new field TODO: remove it
    age = models.SmallIntegerField(null=True)
