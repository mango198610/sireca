"""
URL configuration for sireca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import re_path as url # from django.conf.urls import url # se usaba en la version 3.4
from django.contrib import admin
import django.views.static

from appsireca import views, perfil
from sireca import settings

urlpatterns = []
if settings.DEBUG:
    urlpatterns = [
        url(r'^sireca/static/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.STATIC_ROOT}),
        url(r'^sireca/media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += {
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.panel),
    url(r'^login', views.login_user),
    url(r'^logout$', views.logout_user),
    url(r'^perfil', perfil.view),

}