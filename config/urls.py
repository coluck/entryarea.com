"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

# from app.core.views import redirect_search
from app.core.sitemaps import EASitemap

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('h2pj8mnv3z/', admin.site.urls),
    path('entry/', include('app.entries.urls')),
    path('', include('app.threads.urls')),
    path('', include('app.users.urls')),
    path('', include('app.core.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': {"sitemap": EASitemap}},
         name='django.contrib.sitemaps.views.sitemap')

    # path('<str:string>', redirect_search),
    # path('', include('django.contrib.auth.urls')),
]

# Django Debug Toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('admin/doc/', include('django.contrib.admindocs.urls')),
    ] + urlpatterns
