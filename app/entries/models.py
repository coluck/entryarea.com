import re
from typing import Any, Union

import bleach

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator

from app.core.models import SoftDeletionModel
from app.threads.models import Thread


class Entry(SoftDeletionModel):
    body = models.TextField()
    lang = models.CharField(max_length=5)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='entries')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE,
                               related_name='entries')
    favs = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favs')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'entries'
        ordering = ['id']   # Much more speedy than created_at

    def __str__(self):
        truncated_entry = Truncator(self.body)
        return str(truncated_entry.chars(30))
        # return str(self.id)

    def get_absolute_url(self):
        return reverse('entry:read', args=[self.id])

    def get_body(self):
        p = re.compile(r"\((?:see:|bkz:) ([\w ]*)\)")
        entry = re.sub(p, r"(see: <a href='/s?q=\1'>\1</a>)", self.body)
        return bleach.clean(entry)
        # return mark_safe(self.body)
        # return mark_safe(markdown(self.body, safe_mode='escape'))
        # return markdown(self.body, safe_mode='escape')

    def get_next(self):
        """ Get the next entries count in the thread, used in entry read """
        return Entry.objects.filter(thread=self.thread). \
            filter(created_at__gt=self.created_at).count()

    def get_previous(self):
        """ Get the previous entries count in the thread """
        return Entry.objects.filter(thread=self.thread). \
            filter(created_at__lt=self.created_at).count()

    def get_favorites(self):
        return self.favs.all()

    # def is_faved(self, user):
    #     if user in self.favs:
    #         return True
    #     return False


class Favorite(models.Model):
    id = None
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='favorites')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE,
                              related_name='favorites')
