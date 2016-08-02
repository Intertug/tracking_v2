from django.shortcuts import render
from settings import (VESSEL_CINFIGURATION_URL as vsConf, 
                      VESSELS_POSITION_URL as vsPos, 
                      VISUAL_CONFIGURATION_URL as visualConf,
                      MAP_CONFIGURATION_URL as mapConf)

from webServicesCalls import getXML, getJSON

def country(request, fleet):
    '''
    Controller that recieve a request from the browser and a parameter in the url with the fleetId
    returns a render page with the variables to use in the HTML
    '''
    sessionId = ""
    if (fleet == "0"):#if the fleetId is 0, then blank the string to search
        getData = ""
    else:
        getData = "fleetId=" + fleet
    vesselsPosition = getXML(sessionId, getData, vsPos)
    visualConfig = getJSON("0", visualConf)
    fleetName = "Flota Global"
    #extracts all the fleet Names
    for f in visualConfig["linksmenu"][0]["links"]:
        if fleet == str(f["value"]):
            fleetName = f["label"]
    vesselsIds = []
    #extracts all the vesselsId's
    for vessel in vesselsPosition:
        vesselsIds.append(vessel["id"])
    vesselConfig = []
    #with the vesselsId's creates all the configurations for that ids
    for vessel in vesselsIds:
        vesselConfig.append(getJSON(vessel, vsConf))
    mapConfig = getJSON(fleet, mapConf)
    vars = {"vessels": vesselsPosition, "visual": visualConfig, "map": mapConfig, "vessel": vesselConfig, 
            "fleet": fleetName, "fleetId": fleet}
    return render(request, "country.html", vars)

def index(request):
    return render(request, "index.html")