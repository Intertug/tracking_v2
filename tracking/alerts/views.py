from django.shortcuts import render
import pypyodbc as sql
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (VESSELS_POSITION_URL as vsPos,
                               VISUAL_CONFIGURATION_URL as visualConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData,
                               CONN_STRING as dbString,
                               APPLICATION_ID as appId,
                               LOGGING_URL as LOGIN)
from tracking.util import selectFleetName, validateSession
import datetime
from django.shortcuts import redirect

def alerts(request, fleet):
    '''
    Controller that recieve a request from the browser and a parameter in the url with the fleetId
    returns a render page with the variables to use in the HTML
    '''
    try:
        ui, sessionId = validateSession(request.GET.get('SessionID'), LOGIN, appId, visualConf)
    except:
        return redirect(LOGIN)
    if (fleet == "0"):#if the fleetId is 0, then blank the string to search
        getData = ""
    else:
        getData = "fleetId=" + fleet
    vesselsPosition = getXML(sessionId, getData, vsPos)
    visualConfig = ui
    fleetName = "Flota Global"
    #extracts all the fleet Names
    fleetName = selectFleetName(visualConfig["Menu"]["MenuItem"], fleet)
    #with the vesselsId's creates all the configurations for that ids
    vars = {"vessels": vesselsPosition, "visual": visualConfig, "fleet": fleetName, "fleetId": fleet, "session": sessionId}
    return render(request, "alerts.html", vars)