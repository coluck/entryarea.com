from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetConfirmView, PasswordResetDoneView
from django.db.models import F
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse, reverse_lazy
from django.utils.translation import get_language as lang
from django.utils.translation import ugettext as _
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404

from app.entries.models import Entry, Favorite
from app.users.forms import SignUpForm
from app.users.models import User


class Login(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        messages.success(self.request, _("welcome %(nick)s") %
                         {'nick': self.request.user.username})
        return super().get_success_url()


def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("welcome %(nick)s") %
                             {'nick': user.username})
            return redirect('thread:idx')
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})


class PasswordChange(PasswordChangeView):
    template_name = "auth/password/password_change_form.html"
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, _("Your password was changed.").lower())
        return super().form_valid(form)


class PasswordReset(PasswordResetView):
    email_template_name = "auth/mail/password_reset_email.html"
    template_name = "auth/password/password_reset_form.html"
    # success_url = reverse_lazy('user:password_reset_done')
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request,
                         _("We've emailed you instructions for setting your password, "
                           "if an account exists with the email you entered."
                           " You should receive them shortly.").lower())
        return super().form_valid(form)


class PasswordResetConfirm(PasswordResetConfirmView):
    success_url = "/"
    template_name = "auth/password/password_reset_confirm.html"

    def form_valid(self, form):
        messages.success(self.request,
                         _("Your password has been set.  You may go ahead and log in now.").lower())
        return super().form_valid(form)


def validate_username(request):
    if request.is_ajax():
        username = request.GET.get('username')
        data = {
            'is_taken': User.objects.filter(username__exact=username).exists()
        }
        return JsonResponse(data)


def profile(request, username):
    user = User.objects.get(username__exact=username)
    return render(request, 'auth/profile.html', {'user': user})


class Profile(generic.ListView):
    model = Entry
    context_object_name = 'entries'
    template_name = 'auth/profile.html'
    paginate_by = 15
    paginate_orphans = 3

    def dispatch(self, request, *args, **kwargs):
        self.user = User.objects.\
            filter(username__exact=self.kwargs.get('username')).\
            only('username')[0]
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = super().get_queryset().with_favs(self.request.user)\
            .filter(user=self.user).filter(lang=lang())\
            .annotate(title=F('thread__title'),
                      slug=F('thread__slug'),
                      username=F('user__username')).order_by("-created_at")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_profile'] = self.user
        # context['tags'] = self.user.entries.
        return context


class Favorites(Profile):
    template_name = "auth/favorites.html"

    def get_queryset(self, **kwargs):
        queryset = Entry.objects.get_queryset().with_favs(self.user).\
            filter(favorites__user=self.user).\
            annotate(title=F('thread__title'),
                      slug=F('thread__slug'),
                      username=F('user__username')).order_by("-created_at")
        return queryset
