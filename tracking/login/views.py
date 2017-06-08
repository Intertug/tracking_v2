from django.shortcuts import render
from tracking.settings import (APPLICATION_ID as appId, 
                               CREATE_SESSION_URL as url, 
                               CLOSE_SESSION_URL as close,
                               LOGGING_URL as LOGIN)
from django.shortcuts import redirect
from tracking.webServicesCalls import getSession, closeSession
from django.http import Http404

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
            raise Http404
    
    vars = {}
    return render(request, "login.html", vars)

def logout(request):
    sessionId = request.GET.get('SessionID')
    url = "{}SessionID={}&ApplicationID={}".format(close, sessionId, appId)
    state = closeSession(url)
    if state == "OK_SESSIONCLOSED":
        return redirect(LOGIN)
    else:
        raise Http404