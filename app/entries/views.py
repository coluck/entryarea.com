import json

import bleach
from bleach.sanitizer import ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_STYLES
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, QuerySet
from django.http import Http404, HttpResponseNotFound, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _
from django.views import generic

from .forms import EntryForm, BodyForm
from .models import Entry, Favorite
from ..threads.models import Thread


class EntryRead(generic.DetailView):
    model = Entry
    template_name = 'entries/read.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.get_queryset().annotate(username=F("user__username")) \
            .select_related("thread")
        try:
            entry = queryset.get(pk=pk)
        except ObjectDoesNotExist:
            entry = None
        return entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        context['tags'] = self.get_object().thread.tags.all
        return context


class EntryUpdate(generic.UpdateView):
    model = Entry
    template_name = 'entries/update.html'
    # fields = ['body']
    form_class = EntryForm

    # def form_valid(self, form):
    #     if form.instance.user_id == self.request.user:
    #         return super().form_valid(form)

    # def get_queryset(self):
    #     base_qs = super(EntryUpdate, self).get_queryset()
    #     print(base_qs.filter(user_id=self.request.user))
    #     return base_qs.filter(user_id=self.request.user)

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.body = bleach.clean(entry.body, tags=[])
        entry.updated_at = timezone.now()
        entry.save()
        return redirect('entry:read', pk=entry.pk)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return Http404("you are not allowed to edit this entry")
        return super(EntryUpdate, self).dispatch(request, *args, **kwargs)

    # success_url = '/'

    def get_success_url(self):
        pk = self.kwargs['pk']
        # return '/entry/'+str(id)
        return redirect('entry:read', pk=pk)


class EntryDelete(generic.DeleteView):
    model = Entry
    context_object_name = 'entry'
    template_name = 'entries/confirm_delete.html'
    success_url = '/'

    '''
    def get_success_url(self):
        entry = super(EntryDelete, self).get_object()
        thread = entry.thread
        redirect(thread)
    
    '''

    def get_object(self, queryset=None):
        return self.entry

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.get_queryset().annotate(username=F("user__username")) \
            .select_related('thread')
        try:
            self.entry = queryset.get(id=pk)
        except ObjectDoesNotExist:
            return redirect("entry:read", pk)

        if self.entry.user_id != self.request.user.id:
            messages.error(request, _("this entry is not your. don't even try"))
            return redirect("entry:read", pk)
        return super(EntryDelete, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        thread = self.entry.thread
        self.entry.delete()
        messages.info(request, _("your entry was deleted successfully"))
        return redirect(thread)


@login_required
def add_entry(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    if thread.is_closed:
        messages.error(request, _("this thread is closed don't even try"))
        return redirect(thread)
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.body = bleach.clean(entry.body, tags=[])
            entry.thread = thread
            entry.user = request.user  # entry.user = auth.get_user(request)
            entry.lang = thread.lang   # lang() langs should be same as thread
            entry.created_at = timezone.now()  # removed auto_now_add for adm
            entry.save()

            thread.last_entry = timezone.now()
            thread.save()

            thread_url = reverse('thread:read', kwargs={'slug': slug})
            url = f'{thread_url}?page=last#{entry.id}'
            messages.success(request, _('your entry was published'))
            return redirect(url)
    return redirect(thread)


@login_required
def fav_entry(request, pk):
    entry = Entry.objects.get(pk=pk)
    if request.user not in entry.favs.all():
        entry.favs.add(request.user)
    else:
        entry.favs.remove(request.user)

    return HttpResponse(
        json.dumps({
            "cnt": entry.favs.count()
        })
    )


@login_required
def favorite_entry(request, pk):
    favorite, created = Favorite.objects.get_or_create(user=request.user,
                                                       entry=pk)
    if not created:
        favorite.delete()

    return HttpResponse(
        json.dumps({
            "result": created,
            "count": Favorite.objects.filter(entry_id=pk).count()
        }),
        content_type="application/json")
