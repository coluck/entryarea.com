from django import template

from app.threads.models import Tag

register = template.Library()


@register.simple_tag
def tags(thread):
    return thread.tags.all()


@register.simple_tag
def all_tags():
    return Tag.objects.all()
