from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.utils.translation import get_language as lang
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404

from app.entries.models import Entry
from app.users.forms import SignUpForm
from app.users.models import User


class Login(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('thread:index')
        # TODO: if form is not valid display validation error
    else:
        form = SignUpForm()
    return render(request, 'auth/register.html', {'form': form})


def validate_username(request):
    username = request.GET.get('username')
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
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

    def get_queryset(self, **kwargs):
        self.user = User.objects.\
            filter(username__exact=self.kwargs.get('username')).\
            only('username')[0]

        queryset = super().get_queryset().filter(user=self.user).\
            filter(lang=lang()).annotate(title=F('thread__title'),
                                         slug=F('thread__slug'),
                                         username=F('user__username'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_profile'] = self.user
        return context


def favs(request, username):
    user = get_object_or_404(User, username=username)
    return HttpResponse(user.favs.all())
