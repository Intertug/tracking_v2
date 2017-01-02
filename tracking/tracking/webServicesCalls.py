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

