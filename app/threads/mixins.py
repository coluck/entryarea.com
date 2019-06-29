import datetime as dt
from django.db.models import Count, Q
from django.http import QueryDict
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _

from django.shortcuts import get_object_or_404

from app.threads.models import Thread


# .annotate(is_fav=Count("favorites", filter=Q(favorites__user__in=[self.request.user]))) \

class LangMixin:
    def get_queryset(self, **kwargs):
        queryset = super(LangMixin, self).get_queryset(**kwargs)
        queryset = queryset.filter(lang=lang())

        return queryset


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
        # """
        # # thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        # thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        # queryset = thread.entries.all()
        # query = self.request.GET.get("day", None)
        # if query is not None:
        #     return thread.entries.filter(created_at__day=query)
        # return queryset"""
        # queryset = super().get_queryset(**kwargs)
        # # qd = QueryDict(self.request)
        # qd = self.request.GET
        # # print(qd)
        #
        # if qd.get("search"):
        #     # print("search")
        #     queryset = queryset.filter(body__icontains=qd.get("search"))
        #
        # if qd.get("date"):
        #     queryset = queryset.filter(entries__created_at_starts_with=qd.get("date"))

        queryset = super().get_queryset(**kwargs)
        return queryset


class ThreadIndexMixin:
    def get_queryset(self, **kwargs):
        if self.request.GET.get("week", None):
            cnt = Count("entries",
                        filter=Q(entries__created_at__gt=dt.date.today() -
                                                         dt.timedelta(days=7)) &
                               Q(entries__deleted_at=None)
                        , distinct=True)
            queries = Thread.objects.filter(lang=lang()) \
                          .annotate(cnt=cnt).filter(cnt__gt=0) \
                          .order_by("-last_entry").only('title', 'slug')
        else:
            cnt = Count("entries",
                        filter=Q(entries__deleted_at=None),
                        distinct=True)
            queries = Thread.objects.filter(lang=lang()) \
                          .annotate(cnt=cnt) \
                          .order_by("-cnt").only('title', 'slug')

        return queries

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['label'] = _("all entries")
        if self.request.GET.get("week", None):
            context['label'] = _("weekly entries")

        return context
