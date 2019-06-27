from django import template
from .. import models
from django.shortcuts import redirect, get_object_or_404, render

register = template.Library()


@register.simple_tag
def is_faved(user, entry):
    # return entry.favorites.filter(id=user).exists()

    return user in entry.favs.all()
    # return entry.favs.filter(user__id__in=[user.id])
    # return entry in user.favs.all()


@register.simple_tag
def is_favorited(user, entry):
    favorite, created = models.Favorite.objects\
        .get_or_create(user=user,
            entry=models.Entry.objects.get(id=entry))
    return created


@register.simple_tag
def fav_count(entry):
    return entry.favs.all().count()
