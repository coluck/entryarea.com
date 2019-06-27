from typing import Any, Union

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self) \
            .update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager):
    alive_only: Union[bool, Any]

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()


class ContactMessage(models.Model):
    ADVICE = "ADV"
    COMPLAIN = "COM"
    OTHER = "OTH"

    # MESSAGE_TYPE = [
    #     (ADVICE, _("advice")),
    #     (COMPLAIN, _("complain")),
    #     (OTHER, _("other"))
    # ]
    subject = models.CharField(max_length=64)
    message = models.TextField(max_length=5000)
    # message_type = models.CharField(choices=MESSAGE_TYPE, max_length=3)
    email = models.EmailField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    lang = models.CharField(choices=settings.LANGUAGES, max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        truncated_entry = Truncator(self.message)
        return str(truncated_entry.chars(30))
