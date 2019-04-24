from django.db import models
from django.db.models import Count, Q
from django.utils.functional import SimpleLazyObject

from app.core.models import SoftDeletionManager, SoftDeletionQuerySet


class EntryWithFavQuerySet(models.QuerySet):
    def favs(self, user):
        if user.is_anonymous:
            return
        is_faved = Count('favs', filter=Q(favs__in=[user]))
        return self.annotate(is_faved=is_faved)


class EntryWithFavManager(models.Manager):
    # def get_queryset(self):
    #     return EntryWithFavQuerySet(self.model, using=self._db)
    def get_queryset(self):
        if self.alive_only:
            return EntryWithFavQuerySet(self.model, using=self._db).filter(deleted_at=None)
        return EntryWithFavQuerySet(self.model)

    def favs(self, user):
        return self.get_queryset().favs(user)
