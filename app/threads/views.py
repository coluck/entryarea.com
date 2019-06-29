from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _
from django.views import generic

from app.entries.forms import EntryForm, BodyForm
from app.entries.models import Entry
from app.entries.views import add_entry
from . import api
from .forms import ThreadForm
from .mixins import ThreadMixin, ThreadIndexMixin
from .models import Thread, Tag, PAGINATE


def index(request):
    entries = Entry.objects.all().with_favs(request.user).filter(lang=lang()).\
        annotate(title=F('thread__title'), slug=F('thread__slug'),
                 username=F('user__username')).order_by("?")[:5]
    return render(request, 'threads/idx.html', context={'entries': entries})


class ThreadIndex(ThreadIndexMixin, generic.ListView):
    template_name = 'threads/index.html'
    context_object_name = 'threads'
    paginate_by = 10
    model = Thread

    def get_queryset(self):
        queryset = super().get_queryset().filter(lang=lang())
        return queryset

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return api.api_thread(request, args, kwargs)
        return super().get(request, **kwargs)


@login_required
def newt(request):
    if request.method == "GET":
        return render(request, "threads/new.html")  # TODO :düzelt
    elif request.method == "POST":
        thread_form = ThreadForm(request.POST)
        entry_form = BodyForm(request.POST)

        title = thread_form.clean_title()
        try:
            thread = Thread.objects.get(title=title, lang=lang())
            return add_entry(request, thread.slug)
        except ObjectDoesNotExist:
            if thread_form.is_valid() and entry_form.is_valid():
                thread = Thread(title=title, user=request.user, lang=lang())
                # thread = thread_form.save(commit=False)
                # thread.user = request.user
                # thread.lang = lang()
                thread.save()
                add_entry(request, thread.slug)
                messages.success(request, _('and the thread was created'))
                return redirect(thread)


class ThreadRead(ThreadMixin, generic.ListView):
    model = Entry
    context_object_name = 'entries'
    template_name = 'threads/read.html'
    paginate_by = PAGINATE
    paginate_orphans = 3

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs).with_favs(self.request.user)\
            .filter(thread=self.thread).annotate(username=F('user__username'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EntryForm()
        form.fields['body'].widget.attrs['placeholder'] = \
            _("write about %(title)s") % {'title': str(self.thread.title)}
        context['thread'] = self.thread
        context["form"] = form
        return context


def short_thread_read(request, id):
    thread = get_object_or_404(Thread, id=id)
    return redirect(thread)


class TagIndex(generic.ListView):
    template_name = 'threads/tag-index.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.filter(lang=lang())\
            .annotate(tcnt=Count("threads")).all()


class TagRead(generic.ListView):
    model = Thread
    context_object_name = 'threads'
    template_name = 'threads/tag-read.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["tag"] = self.tag
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.tag.threads.annotate(ecnt=Count("entries"))\
            .order_by("-last_entry")
        return queryset

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            print("dasd")
            return api.api_tag(self.tag.slug, args, kwargs)
        return super().get(request, **kwargs)


def nav_tag_factory(request, lang):
    if request.user.is_superuser:
        tags = Tag.objects.filter(lang=lang).annotate(cnt=Count("threads"))\
            .order_by("-cnt")
        return render(request, "partial/nav/factory.html",
                      context={'tags': tags})
    raise Http404()
