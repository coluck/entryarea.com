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
    path('@<username>/', views.Profile.as_view(), name='profile'),
    path('@<username>/favorites/', views.Favorites.as_view(), name='favorites'),

    path('change-pass/', views.PasswordChange.as_view(), name='password_change'),
    # path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),

    path('reset-pass/', views.PasswordReset.as_view(), name='password_reset'),
    # path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

