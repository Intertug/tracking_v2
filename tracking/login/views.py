from django.shortcuts import render
from tracking.settings import (APPLICATION_ID as appId, CREATE_SESSION_URL as url)
from django.shortcuts import redirect
from tracking.webServicesCalls import getSession

def login(request):
    if request.POST.get("userName") != None and request.POST.get("password") != None:
        user = request.POST.get("userName")
        passw = request.POST.get("password")
        try:
            urlString = "{}ApplicationID={}&DeviceID=&UserName={}&Password={}".format(url, appId, user, passw)
            sessionid = getSession(urlString)
            if len(sessionid) == 36:
                return redirect("/index/?SessionID={}".format(sessionid))
            else:
                vars = {"message": sessionid}
                return render(request, "login.html", vars)
        except:
            pass
    
    vars = {}
    return render(request, "login.html", vars)