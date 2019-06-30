import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from app.threads.models import Thread
from app.entries.models import Entry


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w.+-]+$'
    message = _(
        'enter a nick that contains only 42 characters or fewer.'
        'may contain english letters, numbers, and ./+/-/_ characters.'
    )
    flags = re.ASCII


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class User(AbstractUser):
    first_name = None
    last_name = None
    username_validator = UsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=42,
        unique=True,
        help_text=_('required. 42 characters or fewer. letters, digits and ./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("this nick was taken."),
        },
    )
    # pinned_entry = models.OneToOneField(Entry, on_delete=models.CASCADE,
    #                     related_name="pinned_entry", null=True, blank=True)
    # This is just an example to append a new field
    # age = models.SmallIntegerField(null=True)

    # followed_user = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #                                        related_name="followers", blank=True)
    # followed_thread = models.ManyToManyField(Thread, related_name="followers",
    #                                          blank=True)
    # followed_tag = models.ManyToManyField(Tag, related_name="followers")
    objects = CustomUserManager()
