from django.shortcuts import render
from settings import (VESSEL_CINFIGURATION_URL as vsConf, 
                      VESSELS_POSITION_URL as vsPos, 
                      VISUAL_CONFIGURATION_URL as visualConf,
                      MAP_CONFIGURATION_URL as mapConf, 
                      APPLICATION_ID as appId,
                      LOGGING_URL as LOGIN)
from webServicesCalls import getXML, getJSON
from django.shortcuts import redirect

def country(request, fleet):
    '''
    Controller that recieve a request from the browser and a parameter in the url with the fleetId
    returns a render page with the variables to use in the HTML
    '''
    if request.GET.get('SessionID'):
        sessionId = request.GET.get('SessionID')
    else:
        return redirect(LOGIN)
    getData = "Appid=" + appId
    userUI = getXML(sessionId, getData, visualConf)
    if userUI["query"]["ans"] == "OK_QRY":
        ui = userUI["query"]["rst"]
    else:
        return redirect(LOGIN)
    getData = "fleetId=" + fleet
    vesselsPosition = getXML(sessionId, getData, vsPos)
    visualConfig = ui
    fleetName = "Flota Global"
    #extracts all the fleet Names
    if type(visualConfig["Menu"]["MenuItem"]) == type(dict()):
        pass
    else:
        if type(visualConfig["Menu"]["MenuItem"][0]["MenuItem"]) == type(dict()):
            fleetName = visualConfig["Menu"]["MenuItem"][0]["MenuItem"]["title"]
        else:
            for f in visualConfig["Menu"]["MenuItem"][0]["MenuItem"]:
                if fleet == str(f["url"]):
                    fleetName = f["title"]
    vesselsIds = []
    #extracts all the vesselsId's
    for vessel in vesselsPosition:
        vesselsIds.append(vessel["id"])
    vesselConfig = []
    #with the vesselsId's creates all the configurations for that ids
    for vessel in vesselsIds:
        getData = "vesselid=" + vessel
        configJson = getXML(sessionId, getData, vsConf)
        vesselConfig.append(configJson["configdata"])
    getData = "fleetId=" + fleet
    mapConfig = getXML(sessionId, getData, mapConf)
    mapConfig = mapConfig["configdata"]
    vars = {"vessels": vesselsPosition, "visual": visualConfig, "map": mapConfig, "vessel": vesselConfig, 
            "fleet": fleetName, "fleetId": fleet, "session":sessionId}
    return render(request, "country.html", vars)

def index(request):
    if request.GET.get('SessionID'):
        sessionId = request.GET.get('SessionID')
        getData = "Appid=" + appId
        userUI = getXML(sessionId, getData, visualConf)
        ui = userUI["query"]["rst"]
        if userUI["query"]["ans"] == "OK_QRY":
            return redirect(ui["homeUrl"]+"?SessionID="+sessionId)
        else:
            return redirect(LOGIN)
    else:
        return redirect(LOGIN)
        #return render(request, "index.html")