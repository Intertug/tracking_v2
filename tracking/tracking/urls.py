"""tracking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views
#from django.views.generic import RedirectView

urlpatterns = [
    #url(r'^$', views.index),
    url(r'^$', include('login.urls')),
    #url(r'^$', RedirectView.as_view(url="country/0")),
    url(r'^country/(?P<fleet>[0-9]{1,4})/', views.country),
    url(r'^paths/', include('paths.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^alerts/', include('alerts.urls')),
    url(r'^maneuver/', include('maneuver.urls')),
    #url(r'^login/', include('login.urls')),
    url(r'^index/', views.index),
    #url(r'^admin/', admin.site.urls),
]
