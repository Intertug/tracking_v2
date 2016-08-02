from django.conf.urls import url
from . import views

urlpatterns = [
    
    url(r'^(?P<fleet>[0-9]{1,4})/', views.alerts),
    
]