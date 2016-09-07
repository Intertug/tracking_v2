from django.shortcuts import render
import datetime
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (DAQ_VALUE_URL as daqVal,
                               VESSEL_CINFIGURATION_URL as vsConf, 
                               VISUAL_CONFIGURATION_URL as visualConf,
                               MAP_CONFIGURATION_URL as mapConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData,
                               ALARMS_LOG_URL as alLog)

def paths(request, vessel):
    '''
    Controller that recieve a request from the browser and a parameter in the url with the vesselId
    returns a render page with the variables to use in the HTML
    '''
    sessionId = ""
    getData = "vesselid=" + vessel
    #If in the request comes a POST with a init and final tags, take the content and depending
    #on the content or not, bring a diferent range of dataset
    if request.POST.get("init") != None and request.POST.get("final") != None:
        if request.POST.get("init") != "" and request.POST.get("final") != "":#if there are two dates, take both
            #create a variable dict to render this dates on the input form
            dates = {
                "init": request.POST.get("init"),
                "final": request.POST.get("final")
            }
            getData += "|INIDATE=" + request.POST.get("init")
            getData += "|ENDDATE=" + request.POST.get("final")
        elif request.POST.get("init") == "" and request.POST.get("final") != "":#if there is only final date, search that one
            dates = {
                "init": request.POST.get("final"),
                "final": request.POST.get("final")
            }
            getData += "|INIDATE=" + request.POST.get("final")
            getData += "|ENDDATE=" + request.POST.get("final")
        elif request.POST.get("init") != "" and request.POST.get("final") == "":#if there is just a init date, serach that one
            dates = {
                "init": request.POST.get("init"),
                "final": request.POST.get("init")
            }
            getData += "|INIDATE=" + request.POST.get("init")
            getData += "|ENDDATE=" + request.POST.get("init")
        else:
            pass
    else:
        dates = {
            "init": datetime.datetime.today().isoformat().split("T")[0],
            "final": datetime.datetime.today().isoformat().split("T")[0]
        }
    gpsData = getXML(sessionId, getData, vsGpsData)
    getData = "vesselid=" + vessel
    try:
        dateId = gpsData["coordinates"][-1]["id"]
    except:
        dateId = dates["init"]
    if len(str(dateId)) > 10:
        dateStr = str(dateId)
        dates["value"] = "{}-{}-{} {}:{}:{}".format(dateStr[:4], dateStr[4:6], dateStr[6:8], dateStr[8:10], dateStr[10:12], dateStr[12:14])
    else:
        date1 = datetime.datetime.today().isoformat().split("T")[0]
        date2 = datetime.datetime.today().isoformat().split("T")[1]
        dates["value"] = "{} {}".format(date1, date2[:8])
    getData += "|datestring=" + str(dateId)
    daqValue = getXML(sessionId, getData, daqVal)
    visualConfig = getJSON("0", visualConf)
    vesselConfig = getJSON(vessel, vsConf)
    mapConfig = getJSON(str(vesselConfig["fleetId"]), mapConf)
    alarms_log = getJSON(vessel, alLog)
    vars = {"path": gpsData, "visual": visualConfig, "map": mapConfig, "vessel": vesselConfig, 
            "alarms": alarms_log, "dates": dates, "value": daqValue, "fleetId": vesselConfig["fleetId"]}
    return render(request, "paths.html", vars)