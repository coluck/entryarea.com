from django.urls import path

from app.threads import views
from . import views, admin

app_name = 'thread'

urlpatterns = [
    path('', views.index, name='idx'),
    path('threads/', views.ThreadIndex.as_view(), name='index'),
    # path('threads/create/', views.ThreadCreate.as_view(), name='create-thread'),
    path('t/<slug>/', views.ThreadRead.as_view(), name='read'),
    # path('t/<slug>/search/', views.ThreadRead.as_view(), name='search'),
    path('thread/new/', views.newt, name='new'),
    path('tags/', views.TagIndex.as_view(), name='tags'),
    path('tag/<slug>/', views.TagRead.as_view(), name='tag-read'),
    path('nav_tag_factory/<str:lang>', views.nav_tag_factory),
]
