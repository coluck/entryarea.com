import re
from typing import Any, Union

import bleach

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Count, Q, OuterRef
from django.http import request
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator

from app.core.models import SoftDeletionModel, SoftDeletionManager
from app.threads.models import Thread
from . managers import EntryManager


class Entry(SoftDeletionModel):
    body = models.TextField()
    first_body = models.TextField(null=True, blank=True)  # if entry edited keep first body
    lang = models.CharField(choices=settings.LANGUAGES, max_length=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='entries')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE,
                               related_name='entries')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    objects = EntryManager()

    class Meta:
        verbose_name_plural = 'entries'
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        truncated_entry = Truncator(self.body)
        return str(truncated_entry.chars(30))
        # return str(self.id)

    def get_absolute_url(self):
        return reverse('entry:read', args=[self.id])

    def get_body(self):
        p = re.compile(r"\(((?:see:|bkz:|aka:)) ([\w \W]{0,50})\)")
        entry = re.sub(p, r"(\1 <a href='/s?q=\2'>\2</a>)", self.body)
        # \((bkz:|see:|aka:) (\w[\w ]{0,50})\) ->p
        # ($1 <a href="/s?q=$2>$2</a>") -> entry
        # p = re.compile(r"\((?:bkz:|see:) (\w[\w ]{0,50})\)")
        # entry = re.sub(p, r'(\1 <a href="/s?q=\1>\1</a>")', self.body)

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
        return self.favorites.all()

    def is_faved(self, user_id):
        if user_id in self.favorites.all():
            return True


class Favorite(models.Model):
    id = None
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='favorites')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE,
                              related_name='favorites')

    class Meta:
        unique_together = ('user', 'entry')

# class Like(models.Model):
#     pass