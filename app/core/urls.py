from django.urls import path

from app.core import views

app_name = 'core'

urlpatterns = [
    path('s', views.search),
    path('contact/', views.contact, name='contact'),
    path('set_timezone/', views.set_timezone, name='timezone'),
    path('about/', views.About.as_view(), name='about'),
    path('random-thread/', views.random_thread, name='random'),
]
