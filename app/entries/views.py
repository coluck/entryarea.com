import json
import time

import bleach
from bleach.sanitizer import ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_STYLES
from django.contrib import messages, auth
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
        queryset = self.get_queryset().with_favs(self.request.user)\
            .annotate(username=F("user__username")).select_related("thread")
        try:
            entry = queryset.get(pk=pk)
        except ObjectDoesNotExist:
            entry = None
        return entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        # context['tags'] = self.get_object().thread.tags.all
        return context


class EntryUpdate(generic.UpdateView):
    model = Entry
    template_name = 'entries/update.html'
    form_class = EntryForm

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.updated_at:
            obj.first_body = obj.body
            obj.save()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.body = bleach.clean(entry.body, tags=[])
        entry.updated_at = timezone.now()
        entry.save()
        if entry.is_published:
            messages.success(self.request, message=_("your entry was updated successfully"))
            return redirect('entry:read', pk=entry.pk)
        else:
            return redirect(reverse("user:hidden", self.request.user))


    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            messages.error(request, message=_("what a nice entry isn't it? if is not try to complain."))
            return redirect(obj.thread)
        return super(EntryUpdate, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        qs = Entry.objects.hid_pub()
        obj = qs.get(pk=pk)
        return obj


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
        # queryset = self.get_queryset().annotate(username=F("user__username")) \
        #     .select_related('thread')
        queryset = Entry.objects.hid_pub().annotate(username=F("user__username"))\
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
            if "hide" in request.POST:
                entry.is_published = False
            entry.body = bleach.clean(entry.body, tags=[])
            entry.thread = thread
            entry.user = request.user  # auth.get_user(request)
            entry.lang = thread.lang   # lang() langs should be same as thread
            entry.created_at = timezone.now()  # removed auto_now_add for adm
            entry.save()

            thread.last_entry = timezone.now()
            thread.save()

            thread_url = reverse('thread:read', kwargs={'slug': slug})
            url = f'{thread_url}?page=last#{entry.id}'
            if entry.is_published:
                messages.success(request, _('your entry was published'))
            else:
                messages.success(request, _('your entry was kept as hidden'))
            return redirect(url)
    return redirect(thread)


@login_required
def favorite_entry(request, pk):
    favorite, created = Favorite.objects\
        .get_or_create(user=request.user, entry=Entry.objects.get(id=pk))
    # time.sleep(0.1)
    if not created:
        favorite.delete()

    return HttpResponse(
        json.dumps({
            "result": created,
            "count": Favorite.objects.filter(entry_id=pk).count()
        }),
        content_type="application/json")
