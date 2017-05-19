from django.shortcuts import render
from tracking.settings import (APPLICATION_ID as appId, CREATE_SESSION_URL as url)
from django.shortcuts import redirect
from tracking.webServicesCalls import getSession

def login(request):
    print request
    if request.POST.get("userName") != None and request.POST.get("password") != None:
        user = request.POST.get("userName")
        passw = request.POST.get("password")
        print user, passw
        try:
            urlString = "{}ApplicationID={}&DeviceID=&UserName={}&Password={}".format(url, appId, user, passw)
            sessionid = getSession(urlString)
            print sessionid
            return redirect("/index?SessionID={}".format(sessionid))
        except:
            pass
    
    vars = {}
    return render(request, "login.html", vars)