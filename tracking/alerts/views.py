from django.shortcuts import render
import pypyodbc as sql
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (VESSELS_POSITION_URL as vsPos,
                               VISUAL_CONFIGURATION_URL as visualConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData)
from tracking.settings import CONN_STRING as dbString
import datetime

def alerts(request, fleet):
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
    #with the vesselsId's creates all the configurations for that ids
    vars = {"vessels": vesselsPosition, "visual": visualConfig, "fleet": fleetName, "fleetId": fleet}
    return render(request, "alerts.html", vars)