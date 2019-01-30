from django import template
from .. import models

register = template.Library()


@register.simple_tag()
def is_faved(user):
    return False
