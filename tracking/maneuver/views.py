from django.shortcuts import render
import datetime
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (DAQ_VALUE_URL as daqVal,
                               VESSELS_POSITION_URL as vsPos,
                               VESSEL_CINFIGURATION_URL as vsConf, 
                               VISUAL_CONFIGURATION_URL as visualConf,
                               MAP_CONFIGURATION_URL as mapConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData,
                               ALARMS_LOG_URL as alLog)

def maneuver(request, fleet):

    if request.method == "POST":
        '''
        Controller that recieve a request from the browser
        returns a render page with the variables to use in the HTML
        '''
        sessionId = ""
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
        visualConfig = getJSON("0", visualConf)

        for vessel in vessels:
            sessionId = ""
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
                "vessel": vesselConfig}

#########################
    else:
        '''
        Controller that recieve a request from the browser
        returns a render page with the variables to use in the HTML
        '''
        sessionId = ""
        getData = "fleetId=" + fleet
        vesselsPosition = getXML(sessionId, getData, vsPos)
        visualConfig = getJSON("0", visualConf)
        fleetName = " Maniobras Flota Global"
        #extracts all the fleet Names
        for f in visualConfig["linksmenu"][0]["links"]:
            if fleet == str(f["value"]):
                fleetName = "Maniobras " + f["label"]
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
                "fleet": fleetName, "fleetId": fleet}
    
    return render(request, "maneuver.html", vars)