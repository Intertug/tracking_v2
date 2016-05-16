from django.conf.urls import url
from . import views

urlpatterns = [
    
    url(r'^(?P<vessel>[0-9]{1,4})/', views.paths),
    
]