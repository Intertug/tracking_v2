from django.shortcuts import render
import datetime
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (DAQ_VALUE_URL as daqVal,
                               VESSELS_POSITION_URL as vsPos,
                               VESSEL_CINFIGURATION_URL as vsConf, 
                               VISUAL_CONFIGURATION_URL as visualConf,
                               MAP_CONFIGURATION_URL as mapConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData,
                               ALARMS_LOG_URL as alLog,
                               APPLICATION_ID as appId,
                               LOGGING_URL as LOGIN)
from tracking.util import selectFleetName

def maneuver(request, fleet):

    if request.method == "POST":
        '''
        Controller that recieve a request from the browser
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

        vessels = request.POST.getlist("vessels")
        dateOne = request.POST.get("dateone")
        dateTwo = request.POST.get("datetwo")
        hourOne = request.POST.get("hourone")
        
        if int(hourOne) < 10 and len(hourOne) < 2:
            hourOne = "0" + hourOne
        hourTwo = request.POST.get("hourtwo")

        if int(hourTwo) < 10 and len(hourTwo) < 2:
            hourTwo = "0" + hourTwo

        vesselsData = []
        getData = "fleetId=" + fleet
        mapConfig = getXML(sessionId, getData, mapConf)
        mapConfig = mapConfig["configdata"]
        visualConfig = ui

        for vessel in vessels:
            getData = "vesselid=" + vessel
            #If in the request comes a POST with a init and final tags, take the content and depending
            #on the content or not, bring a diferent range of dataset
            getData += "|INIDATE=" + str(dateOne) + " " + str(hourOne) + ":00:00"
            getData += "|ENDDATE=" + str(dateTwo) + " " + str(hourTwo) + ":00:00"           
            gpsData = getXML(sessionId, getData, vsGpsData)
            daqValue = getXML(sessionId, getData, daqVal)
            getData = "vesselid=" + vessel
            vesselConfig = getXML(sessionId, getData, vsConf)
            vesselConfig = vesselConfig["configdata"]
            data = { "vesselName": vesselConfig["vesselname"],
                     "path": gpsData,
                     "values": daqValue,
                    }
            vesselsData.append(data)
        vars = {"vessels": vesselsPosition, "data": vesselsData, "visual": visualConfig, "map": mapConfig, "fleetId": fleet,
                "vessel": vesselConfig, "session": sessionId}

#########################
    else:
        '''
        Controller that recieve a request from the browser
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
        fleetName = selectFleetName(visualConfig["Menu"]["MenuItem"], fleet)
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
                "fleet": fleetName, "fleetId": fleet, "session": sessionId}
    
    return render(request, "maneuver.html", vars)