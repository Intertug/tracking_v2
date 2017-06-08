import urllib
import xml.etree.ElementTree as ET
import json

def getXML(si, gd, urlString):
    '''
    Function to call the webservice with a sessionID and a getData param given 
    and return a Json dict with the data
    '''
    url = urlString
    sessionId = si
    getData = gd
    params = "SessionID=" + sessionId
    params += "&GetData=" + getData
    url += params
    try:
        openUrl = urllib.urlopen(url)
    except:
        print "Error calling XML service"
    data = openUrl.read()
    try:
        tree = ET.fromstring(data) #the Json is inside an XML, first node 
    except:
        print "Error readind the XML"
    dataJson = json.loads(tree.text)
    try:
        extract = dataJson["vessels"]["vessel"]
    except:
        extract = dataJson
    return extract

def getJSON(id, urlString):
    '''
    Function to call the webservice with a Id given 
    and return a Json dict with the data
    '''
    url = urlString
    fleetId = id
    url += fleetId
    try:
        openUrl = urllib.urlopen(url)
    except:
        print "Error calling JSON service" 
    data = openUrl.read()
    dataJson = json.loads(data)
    return dataJson

def getSession(url):
    try:
        openUrl = urllib.urlopen(url)
    except:
        return "Error calling XML service"
    data = openUrl.read()
    if data.find("SESSIONUID") != -1:
        openTag = data.find("SESSIONUID")
        closeTag = data.find("/SESSIONUID")
        sessionid = data[openTag+len("SESSIONUID")+4:closeTag-4]
    else:
        return "Invalid user/pass"
    return sessionid

def closeSession(url):
    try:
        openUrl = urllib.urlopen(url)
    except:
        return "Error calling XML service"
    data = openUrl.read()
    if data.find("ANS") != -1:
        openTag = data.find("ANS")
        closeTag = data.find("/ANS")
        state = data[openTag+len("ANS")+4:closeTag-4]
    else:
        return "Error Reading XML"
    return state
    