from django.urls import path

from app.core import views

app_name = 'core'

urlpatterns = [
    path('s', views.Search),
    path('contact/', views.contact),
    path('success/', views.success, name='success')
]
