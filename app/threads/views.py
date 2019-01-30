import json
import random

from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language as lang
from django.views import generic

from app.entries.forms import EntryForm
from app.entries.models import Entry
from .forms import ThreadForm
from .models import Thread, Tag, PAGINATE


def index():
    entries = Entry.objects.filter(lang=lang())


class ThreadIndex(generic.ListView):
    template_name = 'threads/index.html'
    context_object_name = 'threads'

    paginate_by = 10
    # queryset = Thread.objects.all()

    def get_queryset(self):
        return Thread.objects.filter(lang=lang())

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

    queries = Thread.objects.filter(lang=lang())[:20]
    for query in queries:
        results['title'] = query.title
        results['slug'] = query.slug
        results['cnt'] = query.get_entry_count()
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
    return redirect(new)


class ThreadRead(generic.ListView):
    model = Entry
    context_object_name = 'entries'
    template_name = 'threads/read.html'
    paginate_by = PAGINATE

    # form.fields['body'].widget.attrs['placeholder'] = "Hello World"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        tags = thread.tags.all()
        threads = Thread.objects.filter(lang=lang())[:15]
        form = EntryForm()
        form.fields['body'].widget.attrs['placeholder'] =\
            "en light us about " + thread.title

        context['thread'] = thread
        context['tags'] = tags
        context['threads'] = threads
        context["form"] = form
        return context

    def get_queryset(self):
        # thread = Thread.objects.get(slug=self.kwargs.get('slug'))
        thread = get_object_or_404(Thread, slug=self.kwargs.get('slug'))
        queryset = thread.entries.all()
        query = self.request.GET.get("day", None)
        if query is not None:
            return thread.entries.filter(created_at__day=query)
        return queryset


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
