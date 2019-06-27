from django.urls import path

from app.entries import views


app_name = 'entry'

urlpatterns = [
    path('<int:pk>/', views.EntryRead.as_view(), name='read'),
    path('edit/<int:pk>/', views.EntryUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', views.EntryDelete.as_view(), name='delete'),

    path('t/<slug>/entry', views.add_entry, name='create'),

    # path('fav/<int:pk>/', views.fav_entry, name='favorite'),
    path('favorite/<int:pk>/', views.favorite_entry, name='favorited'),
]
