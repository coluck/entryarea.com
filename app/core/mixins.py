from django.utils.translation import get_language as lang


class LangMixin:
    def get_queryset(self, **kwargs):
        queryset = super(LangMixin, self).get_queryset(**kwargs)
        queryset = queryset.filter(lang=lang())

        return queryset
