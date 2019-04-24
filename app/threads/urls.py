from django.urls import path

from app.threads import views
from . import views, admin

app_name = 'thread'

urlpatterns = [
    path('', views.index),
    path('threads/', views.ThreadIndex.as_view(), name='index'),
    # path('api_threads', views.api_thread),
    path('threads/create/', views.ThreadCreate.as_view(), name='create-thread'),
    path('thread/new/', views.newt, name='new'),
    # path('thread/create', views.thread_create, name='create'),
    # path('thread/create/<str:title>', views.create, name='create'),
    path('t/<slug>/', views.ThreadRead.as_view(), name='read'),
    # path('t/<slug>/entry', views.addEntry, name='fun-create-entry'),

    path('tags/', views.TagIndex.as_view(), name='tags'),
    path('tag/<slug>/', views.TagRead.as_view(), name='tag-read'),
    path('api/<str:now_all>/', views.api),
]
