from django.http import QueryDict
from django.utils.translation import get_language as lang

from django.shortcuts import get_object_or_404

from app.threads.models import Thread


# .annotate(is_fav=Count("favorites", filter=Q(favorites__user__in=[self.request.user]))) \

class ThreadMixin:
    def dispatch(self, request, *args, **kwargs):
        self.thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        session_key = 'viewed_thread_{}'.format(self.thread.pk)
        if not self.request.session.get(session_key, False):
            self.thread.views += 1
            self.thread.save()
            self.request.session[session_key] = True

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        """
        # thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        queryset = thread.entries.all()
        query = self.request.GET.get("day", None)
        if query is not None:
            return thread.entries.filter(created_at__day=query)
        return queryset"""
        queryset = super().get_queryset(**kwargs)
        # qd = QueryDict(self.request)
        qd = self.request.GET
        # print(qd)

        if qd.get("search"):
            # print("search")
            queryset = queryset.filter(body__icontains=qd.get("search"))

        if qd.get("date"):
            queryset = queryset.filter(entries__created_at_starts_with=qd.get("date"))

        return queryset


class LangMixin:
    def get_queryset(self, **kwargs):
        queryset = super(LangMixin, self).get_queryset(**kwargs)
        queryset = queryset.filter(lang=lang())

        return queryset
