from django.db import models
from django.db.models import Count, Q, OuterRef, Exists
from django.utils.functional import SimpleLazyObject

from app.core.models import SoftDeletionManager, SoftDeletionQuerySet


class EntryQuerySet(SoftDeletionQuerySet):
    def with_favs(self, user=None):
        qs = super(SoftDeletionQuerySet, self)\
            .annotate(fav_cnt=Count("favorites"))
        if user.is_authenticated:
            from app.entries.models import Favorite
            is_fav = Favorite.objects.filter(
                entry_id=OuterRef('pk'),
                user_id=user.id
            )
            qs = qs.annotate(is_faved=Exists(is_fav))
        return qs


class EntryManager(SoftDeletionManager):
    def get_queryset(self, **kwargs):
        return EntryQuerySet(self.model).filter(deleted_at=None)\
            .filter(is_published=True).defer("deleted_at", "first_body", "is_published")

    def hidden(self):
        qs = super().get_queryset()
        return qs.filter(is_published=False).defer("deleted_at", "first_body")

    def hid_pub(self):
        return EntryQuerySet(self.model).filter(deleted_at=None)\
            .defer("deleted_at", "first_body")

    '''
    def fav_qs(self, user=None):
        qs = super().get_queryset()
        from app.entries.models import Favorite
        is_fav = Favorite.objects.filter(
            entry_id=OuterRef('pk'),
            user_id=user.id
        )
        return qs.annotate(fav_cnt=Count("favorites")) \
                 .annotate(is_faved=Exists(is_fav))
    '''


'''
class HiddenManager(SoftDeletionManager):
    def get_queryset(self):
        pass
'''