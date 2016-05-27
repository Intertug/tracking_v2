from django.shortcuts import render
import urllib
import xml.etree.ElementTree as ET
import json
from tracking.views import mapConfiguration, vesselConfiguration, visualConfiguration

def getVesselGpsData(si, gd):
    
    url= "http://190.242.119.122:82/sioservices/daqonboardservice.asmx/GetVesselGpsData?"
    sessionId = si
    getData = gd
    params = "SessionID=" + sessionId
    params += "&GetData=" + getData
    url += params
    try:
        openUrl = urllib.urlopen(url)
    except:
        print "Error calling getVesselGpsData"
    data = openUrl.read()
    tree = ET.fromstring(data)
    dataJson = json.loads(tree.text)
    return dataJson

def alarmsLog(vi):

    url= "http://nautilus.intertug.com:8080/api/alarmsLog/"
    vesselId = vi
    url += vesselId
    try:
        openUrl = urllib.urlopen(url)
    except:
        print "Error calling alarmsLog"
    data = openUrl.read()
    dataJson = json.loads(data)
    return dataJson

def paths(request, vessel):

    sessionId = ""
    getData = "vesselid=" + vessel
    if request.POST.get("init") != None and request.POST.get("final") != None:
        if request.POST.get("init") != "" and request.POST.get("final") != "":
            getData += "|INIDATE=" + request.POST.get("init")
            getData += "|ENDDATE=" + request.POST.get("final")
        elif request.POST.get("init") == "" and request.POST.get("final") != "":
            getData += "|INIDATE=" + request.POST.get("final")
            getData += "|ENDDATE=" + request.POST.get("final")
        elif request.POST.get("init") != "" and request.POST.get("final") == "":
            getData += "|INIDATE=" + request.POST.get("init")
            getData += "|ENDDATE=" + request.POST.get("init")
        else:
            pass
    gpsData = getVesselGpsData(sessionId, getData)
    visualConfig = visualConfiguration("0")
    vesselConfig = vesselConfiguration(vessel)
    mapConfig = mapConfiguration(str(vesselConfig["fleetId"]))
    alarms_log = alarmsLog(vessel)
    vars = {"path": gpsData, "visual": visualConfig, "map": mapConfig, "vessel": vesselConfig, "alarms": alarms_log}
    return render(request, "paths.html", vars)