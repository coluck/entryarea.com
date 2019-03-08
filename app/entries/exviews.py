import bleach
from bleach.sanitizer import ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_STYLES
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, QuerySet
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _
from django.views import generic

from .forms import EntryForm
from .models import Entry
from ..threads.models import Thread


class Entryread(generic.View):
    def get(self):
        try:
            pk = self.kwargs.get('pk')
            entry = Entry.objects.filter(id=pk)
        except Entry.DoesNotExist:
            entry = None
        return render(self.request, 'entries/read.html', {'entry': entry})


class EntryRead(generic.DetailView):
    model = Entry
    template_name = 'entries/read.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.get_queryset().annotate(username=F("user__username")).select_related("thread")
        try:
            entry = queryset.get(pk=pk)
        except ObjectDoesNotExist:
            entry = None
        return entry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
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
    template_name = 'entries/confirm_delete.html'
    success_url = '/'

    '''
    def get_success_url(self):
        entry = super(EntryDelete, self).get_object()
        thread = entry.thread
        redirect(thread)


    def get_object(self, queryset=None):
        obj = super(EntryDelete, self).get_object()
        if not obj.user == self.request.user:
            raise Http404
        return obj
    '''

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            return Http404()
        return super(EntryDelete, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        entry = self.get_object()
        thread = entry.thread
        if entry.user != self.request.user:
            return Http404()
        Entry.objects.filter(id=entry.id).delete()
        return redirect(thread)
        # return super(EntryDelete, self).delete(request, *args, *kwargs)


@login_required
def add_entry(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    if thread.is_closed:
        return redirect(thread)
    thread_url = thread.get_absolute_url()
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            '''
            entry.body = bleach.clean(form.cleaned_data['body'],
                                      tags=ALLOWED_TAGS,
                                      attributes=ALLOWED_ATTRIBUTES,
                                      styles=ALLOWED_STYLES,
                                      strip=False, strip_comments=True)
            '''
            # entry.body = request.POST['body']
            # entry.body = strip_tags(form.cleaned_data['body'])
            # entry.body = escape(form.cleaned_data['body'])
            entry.thread = thread
            entry.user = request.user
            entry.lang = lang()
            # entry.user = auth.get_user(request)
            entry.save()

            thread.last_entry = timezone.now()
            thread.save()

            # thread_url = reverse('thread:read', kwargs={'slug': slug})
            url = '{url}?page={page}'.format(
                url=thread_url,
                page=thread.get_page_count()
            )
            messages.success(request, _('your entry was published'))
            return redirect(url)
        else:
            redirect(thread_url)
    return redirect(thread_url)


@login_required
def fav_entry(request, pk):
    entry = Entry.objects.get(pk=pk)
    if request.user not in entry.favs.all():
        entry.favs.add(request.user)

    return redirect(entry.thread)
