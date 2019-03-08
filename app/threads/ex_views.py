import datetime
import json
import random

from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, F, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language as lang
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
        tec = Count('entries', filter=Q(entries__created_at__startswith=datetime.date.today()))
        return Thread.objects.filter(lang=lang()).annotate(ecnt=tec)  # Count('entries'))

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


class ThreadCreate(LoginRequiredMixin, generic.CreateView):
    model = Thread
    form_class = ThreadForm
    template_name = 'threads/create.html'

    def post(self, request, *args, **kwargs):
        new = Thread(title=request.POST['title'].lower(), user=request.user,
                     lang=lang())
        new.save()
        messages.success(request, 'your thread was published successfully')
        return redirect(new)


'''
def thread_create(request):
    pass
'''


def create(request, title):
    new = Thread(title=title.lower(), user=request.user, lang=lang())
    new.save()

    entry = Entry(body=request.POST['body'], user=request.user, thread=new,
                  lang=lang())
    entry.save()

    new.last_entry = timezone.now()
    new.save()

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


class ThreadCreateNew(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


class ThreadRead(generic.ListView):
    model = Entry
    context_object_name = 'entries'
    template_name = 'threads/read.html'
    paginate_by = PAGINATE

    def get_queryset(self, **kwargs):
        """
        # thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        queryset = thread.entries.all()
        query = self.request.GET.get("day", None)
        if query is not None:
            return thread.entries.filter(created_at__day=query)
        return queryset"""
        self.thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        # queryset = thread.entries.only('user__username', 'body', 'created_at', 'updated_at')
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter(thread=self.thread).select_related('user')
        #  .annotate(username=F('user__username'))  # in my opinion more
        #  convenient should be edited entry.html TODO: do it
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        tags = self.thread.tags.all()
        # threads = Thread.objects.filter(lang=lang())[:15]
        # today_cnt = Count('entries', filter=Q(entries__created_at__startswith=str(datetime.date.today())))
        threads = Thread.objects.only('title', 'slug').annotate(tecnt=Count('entries'))[:30]
        form = EntryForm()
        form.fields['body'].widget.attrs['placeholder'] = \
            "en light us about " + self.thread.title

        context['thread'] = self.thread
        context['tags'] = tags
        context['threads'] = threads
        context["form"] = form
        return context


class TagIndex(generic.ListView):
    template_name = 'threads/tags.html'
    context_object_name = 'tags'

    def get_queryset(self):
        return Tag.objects.filter(lang=lang())


class TagRead(generic.ListView):
    model = Thread
    context_object_name = 'tag_threads'
    template_name = 'threads/tag-read.html'

    def get_context_data(self, **kwargs):
        tag = Tag.objects.get(label=self.kwargs.get('label'))
        kwargs['tag'] = tag

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        tag = Tag.objects.get(label=self.kwargs.get('label'))
        queryset = tag.thread.all()

        return queryset

    def get(self, request, *args, **kwargs):
        if request.is_ajax:
            tag = Tag.objects.get(label=self.kwargs.get('label'))
            # return api_tag_thread(request, tag)
        return super().get(request, **kwargs)


"""
def api_tag_thread(request, tag):
    # threads = Thread.objects.all().values('title', 'slug')[:10]
    # t_list = list(threads)
    # return JsonResponse(t_list, safe=False)

    results = {}
    lis = []

    queries = Thread.objects.filter(lang=lang(),
                                    tags__thread__tags__exact=tag)[:20]
    for query in queries:
        results['title'] = query.title
        results['slug'] = query.slug
        results['cnt'] = query.get_entry_count()
        lis.append(results.copy())

    res = json.dumps(lis)
    mimetype = 'application/json'

    return HttpResponse(res, mimetype)
"""
