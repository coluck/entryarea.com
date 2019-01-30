from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

app_name = 'user'

urlpatterns = [
    # path('enter/', auth_views.LoginView.
    #      as_view(template_name='auth/login.html'), name='login'),
    path('enter/', views.Login.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ajax/validate_username', views.validate_username,
         name='validate_username'),
    path('@<username>', views.profile, name='profile')
]

