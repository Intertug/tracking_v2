from django.conf.urls import url
from . import views

urlpatterns = [
    
    url(r'^fuel/(?P<fleet>[0-9]{1,2})/(?P<vessel>[0-9]{1,4})/', views.consumption),
    url(r'^distance/(?P<fleet>[0-9]{1,2})/(?P<vessel>[0-9]{1,4})/', views.distance),
    
]