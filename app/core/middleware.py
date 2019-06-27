import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from django.utils import translation


class SubdomainLanguageMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    """
    Set the language for the site based on the subdomain the request
    is being served on. For example, serving on 'en.domain.com' would
    make the language English (en).
    """
    LANGUAGES = ['tr', 'en']

    def __call__(self, request):
        host = request.get_host().split('.')
        if host and host[0] in self.LANGUAGES:
            lang = host[0]
            translation.activate(lang)
            request.LANGUAGE_CODE = lang
        response = self.get_response(request)
        return response


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
