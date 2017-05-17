from django.shortcuts import render
from tracking.settings import APPLICATION_ID as appId

def login(request):
    if request.POST.get("userName") and request.POST.get("password"):
        pass
