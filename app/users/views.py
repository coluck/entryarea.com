from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views import generic
from django.shortcuts import render, redirect

from app.entries.models import Entry
from app.users.forms import SignUpForm
from app.users.models import User


class Login(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect('thread:index')

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


