from django.shortcuts import redirect
from webServicesCalls import getXML

def selectFleetName(item, fleet):
    fleetName = "Flota Global"
    if type(item) == type(dict()):
        pass
    else:
        if type(item[0]["MenuItem"]) == type(dict()):
            fleetName = item[0]["MenuItem"]["title"]
        else:
            for f in item[0]["MenuItem"]:
                if fleet == str(f["url"]):
                    fleetName = f["title"]
    
    return fleetName

def validateSession(sessionId, LOGIN, appId, visualConf):
    getData = "Appid=" + appId
    userUI = getXML(sessionId, getData, visualConf)
    if userUI["query"]["ans"] == "OK_QRY":
        ui = userUI["query"]["rst"]
    else:
        return "No Query"
    return ui, sessionId
    