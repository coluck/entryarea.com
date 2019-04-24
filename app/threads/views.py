import datetime
import json
import random

from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, F, Max
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _
from django.views import generic, View

from app.entries.forms import EntryForm, BodyForm
from app.entries.models import Entry
from app.entries.views import add_entry
from .forms import ThreadForm, TitleForm
from .models import Thread, Tag, PAGINATE


def index(request):
    entries = Entry.objects.filter(lang=lang()).\
        annotate(title=F('thread__title'), slug=F('thread__slug'),
                 username=F('user__username')).\
        order_by("?")[:7]
    return render(request, 'threads/idx.html', context={'entries': entries})

    # max_id = Entry.objects.aggregate(max_id=Max("id"))['max_id']
    # random_list = random.sample([i for i in range(max_id)], 30)
    # entries = Entry.objects.filter(lang=lang()).filter(id__in=random_list).select_related('thread')[:7]
    return render(request, 'threads/idx.html', context={'entries': entries})


class ThreadIndex(generic.ListView):
    template_name = 'threads/index.html'
    context_object_name = 'threads'
    paginate_by = 10

    def get_queryset(self):
        # tec = Count('entries', filter=Q(entries__created_at__startswith=datetime.date.today()))
        ecnt = Count('entries')
        return Thread.objects.filter(lang=lang()).annotate(ecnt=ecnt).order_by("-ecnt")  # Count('entries'))

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return api_thread(request)
        return super().get(request, **kwargs)


def api_thread(request):
    # threads = Thread.objects.all().values('title', 'slug')[:10]
    # t_list = list(threads)
    # return JsonResponse(t_list, safe=False)

    results = {}
    lis = []

    queries = Thread.objects.filter(lang=lang()).only('title', 'slug')[:20]

    for query in queries:
        results['title'] = query.title
        results['slug'] = query.slug
        results['cnt'] = query.entries.count()
        lis.append(results.copy())

    res = json.dumps(lis)
    mimetype = 'application/json'

    return HttpResponse(res, mimetype)


def api(request, now_all):
    if request.is_ajax():
        # # tec = Count('entries', filter=Q(entries__created_at__startswith=
        # #                                 datetime.date.today()))
        # # threads = Thread.objects.only('title', 'slug').filter(lang=lang())\
        # #     .annotate(tecnt=tec)[:30]
        # threads = Thread.objects.only('title', 'slug').filter(lang=lang())\
        #     .annotate(ecnt=Count("entries",
        #         filter=Q(entries__created_at__startswith=datetime.date.today()),
        #         distinct=True)).order_by("-ecnt")

        results = {}
        lis = []
        if now_all == "all":
            queries = Thread.objects.filter(lang=lang()) \
                .annotate(cnt=Count("entries"))\
                .order_by("-cnt").only('title', 'slug')[:20]

        elif now_all == "now":
            # By now is implemented 7 days duration change it to 1 day when site gets popular
            queries = Thread.objects.filter(lang=lang()) \
                .annotate(cnt=Count("entries",
                    # filter=Q(entries__created_at__startswith=datetime.date.today()),
                    filter=Q(entries__created_at__gt=datetime.date.today()-datetime.timedelta(days=7)),
                    distinct=True)).order_by("-cnt").only('title', 'slug')[:20]
        else:
            return Http404()

        for query in queries:
            results['title'] = query.title
            results['slug'] = query.slug
            results['cnt'] = query.cnt
            lis.append(results.copy())

        res = json.dumps(lis)
        mimetype = 'application/json'

        return HttpResponse(res, mimetype)


class ThreadCreate(LoginRequiredMixin, generic.CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'threads/create.html'

    def post(self, request, *args, **kwargs):
        new = Thread(title=request.POST['title'].lower(), user=request.user,
                     lang=lang())
        new.save()
        messages.success(request, _('your thread was published successfully'))
        return redirect(new)


def new(request, title):
    if request.method == "GET":
        try:
            thread = Thread.objects.get(title=title, lang=lang())
            return redirect(thread)
        except Thread.DoesNotExist:
            data = {"title": title}
            thread_form = TitleForm(data)
            if thread_form.is_valid():
                entry_form = BodyForm()
                entry_form.fields['body'].widget.attrs['placeholder'] = \
                    "en light us about " + title

                context = {"tform": thread_form, "eform": entry_form, "title": title}
                return render(request, "threads/new.html", context=context)

    if request.method == "POST":
        thread_form = TitleForm(request.POST)
        entry_form = BodyForm(request.POST)
        if thread_form.is_valid() and entry_form.is_valid():
            new_thread = Thread(title=thread_form.cleaned_data['title'],
                                user=request.user, lang=lang())
            new_thread.last_entry = timezone.now()
            new_thread.save()

            add_entry(request, new_thread.slug)
            messages.success(request, 'and the thread was created')
            return redirect(new_thread)
        else:
            return redirect("/")


def newt(request):
    if request.method == "GET":
        return render("threads:new")  # TODO :düzelt
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
                return redirect(thread)


class ThreadRead(generic.ListView):
    model = Entry
    context_object_name = 'entries'
    template_name = 'threads/read.html'
    paginate_by = PAGINATE
    paginate_orphans = 3

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
        # self.thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))

        queryset = super().get_queryset(**kwargs).filter(thread=self.thread)\
            .annotate(username=F('user__username'))
        # print(self.request.GET.get('re'))
        if self.request.user.is_authenticated:
            is_faved = Count('favs', filter=Q(favs__in=[self.request.user]))
            queryset = queryset.annotate(is_faved=is_faved)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tags = self.thread.tags.all()

        form = EntryForm()
        form.fields['body'].widget.attrs['placeholder'] = \
            _("en light us about ") + self.thread.title

        context['thread'] = self.thread
        context['tags'] = tags
        context["form"] = form
        return context


class TagIndex(generic.ListView):
    template_name = 'threads/tag-index.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.filter(lang=lang())\
            .annotate(tcnt=Count("thread")).all()


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
        kwargs["thread_cnt"] = self.tag.thread.count()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.tag.thread.annotate(ecnt=Count("entries"))\
            .order_by("-last_entry")
        return queryset

    # def get(self, request, *args, **kwargs):
    #     if request.is_ajax:
    #         tag = Tag.objects.filter(lang=lang())\
    #             .filter(label=self.kwargs.get('label'))
    #         # return api_tag_thread(request, tag)
    #     return super().get(request, **kwargs)
