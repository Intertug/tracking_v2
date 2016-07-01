from django.shortcuts import render
import urllib
import xml.etree.ElementTree as ET
import json
from tracking.views import mapConfiguration, vesselConfiguration, visualConfiguration
import datetime

def getDaqValue(si, gd):
    '''
    Function to call the webservice GetDaqValue/ with a vesselId and a getData param given 
    and return a Json dict with the data
    '''
    url= "http://190.242.119.122:82/sioservices/daqonboardservice.asmx/GetDaqValue?"
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
    tree = ET.fromstring(data) #the Json is inside an XML, first node
    dataJson = json.loads(tree.text)
    return dataJson

def getVesselGpsData(si, gd):
    '''
    Function to call the webservice GetVesselGpsData/ with a vesselId and a getData param given 
    and return a Json dict with the data
    '''
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
    tree = ET.fromstring(data) #the Json is inside an XML, first node
    dataJson = json.loads(tree.text)
    return dataJson

def alarmsLog(vi):
    '''
    Function to call the webservice alarmsLog/ with a vesselId param given
    and return the Json data
    '''
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
    gpsData = getVesselGpsData(sessionId, getData)
    getData = "vesselid=" + vessel
    try:
        dateId = gpsData["coordinates"][-1]["id"]
    except:
        dateId = dates["init"]
    getData += "|datestring=" + str(dateId)
    daqValue = getDaqValue(sessionId, getData)
    dates["value"] = daqValue["_dte"]
    visualConfig = visualConfiguration("0")
    vesselConfig = vesselConfiguration(vessel)
    mapConfig = mapConfiguration(str(vesselConfig["fleetId"]))
    alarms_log = alarmsLog(vessel)
    vars = {"path": gpsData, "visual": visualConfig, "map": mapConfig, "vessel": vesselConfig, 
            "alarms": alarms_log, "dates": dates, "value": daqValue}
    return render(request, "paths.html", vars)