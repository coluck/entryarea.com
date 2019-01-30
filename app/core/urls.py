from django.urls import path

from app.core import views

app_name = 'core'

urlpatterns = [
    path('', views.search),
]
