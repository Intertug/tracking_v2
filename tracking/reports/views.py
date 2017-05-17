from django.shortcuts import render
import pypyodbc as sql
from tracking.webServicesCalls import getXML, getJSON
from tracking.settings import (VESSELS_POSITION_URL as vsPos,
                               VISUAL_CONFIGURATION_URL as visualConf, 
                               VESSEL_GPS_DATA_URL as vsGpsData,
                               CONN_STRING as dbString,
                               APPLICATION_ID as appId,
                               LOGGING_URL as LOGIN)
import datetime
import sys
import math
from tracking.util import validateSession
from django.shortcuts import redirect

def distance(request, vessel, fleet):
    '''
    Controler that recieve a request from the browser and two parameters in the url with the fleetId and vesselId
    returns a render page with the variables to use in the HTML
    '''
    try:
        ui, sessionId = validateSession(request.GET.get('SessionID'), LOGIN, appId, visualConf)
    except:
        return redirect(LOGIN)
    getData = "vesselid=" + vessel
    data = []
    #sees if in the request comes a POST to create a biger report and the range of the report
    if request.POST.get("dateone") and request.POST.get("datetwo"):
        dateOne = request.POST.get("dateone")
        dateTwo = request.POST.get("datetwo")
        dates = {
            "init": dateOne,
            "final": dateTwo
        }
        #creates a datetimes from strings of the request
        dateOne = datetime.date(int(dateOne.split("-")[0]), int(dateOne.split("-")[1]), int(dateOne.split("-")[2]))
        dateTwo = datetime.date(int(dateTwo.split("-")[0]), int(dateTwo.split("-")[1]), int(dateTwo.split("-")[2]))
        #loops through the date range and calls the webservice for each date
        while dateOne <= dateTwo:
            dateTemp = dateOne.isoformat()
            getData += "|INIDATE=" + dateTemp
            getData += "|ENDDATE=" + dateTemp
            gpsData = getXML(sessionId, getData, vsGpsData)
            data.append(createDistance(gpsData["coordinates"], dateTemp))
            getData = "vesselid=" + vessel
            dateOne += datetime.timedelta(days=1)
    else:
        #just brings the data from today
        dateOne = datetime.datetime.today().isoformat().split("T")[0]
        dates = {
            "init": dateOne,
            "final": dateOne
        }
        gpsData = getXML(sessionId, getData, vsGpsData)
        data.append(createDistance(gpsData["coordinates"], dateOne))
    getData = "fleetId=" + fleet
    vesselsPosition = getXML(sessionId, getData, vsPos)
    vesselsNames = []
    #gets all the names and vesselsIds
    for v in vesselsPosition:
        var = {
            "name": v["vesselname"],
            "id": v["id"]
        }
        vesselsNames.append(var)
    visualConfig = ui
    vars = {"fleetId": fleet, "data": data, "names": vesselsNames, "visual": visualConfig, "vessel": vessel, "dates": dates, 
            "session": sessionId}
    return render(request, "distanceReport.html", vars)

def createDistance(coordinates, date):
    '''
    Function that creates a dict with the totals of distance traveled and the average speed of the range
    from the coordinates (lat, lon) of the day using the Haversine formula
    returns a List of dicts with the totals
    '''
    speeds = []
    distances = []
    radious = 6378 #earth radiuos
    #loops through the list of points (lat, lon) of the date
    for c in range(len(coordinates) - 1):
        lat1 = coordinates[c]["position"]["lat"]
        lon1 = coordinates[c]["position"]["lon"]
        lat2 = coordinates[c+1]["position"]["lat"]
        lon2 = coordinates[c+1]["position"]["lon"]
        #uses the Haversine formula
        a = math.cos(math.radians(90 - lat1)) * math.cos(math.radians(90 - lat2))
        b = math.sin(math.radians(90 - lat1)) * math.sin(math.radians(90 - lat2)) * math.cos(math.radians(lon1 - lon2)) 
        try:
            val = math.acos(a + b) * radious #could throw a math error
        except:
            val = 0
        distances.append(val) 
        speeds.append(coordinates[c]["speed"])
    try:
        avgSpeed = round(sum(speeds) / len(speeds), 2)#could throw 0 division
    except:
        avgSpeed = 0.0
    distanceSpeed = {
        "distance": round(sum(distances) * 0.539956803456, 2), #convert the distance in Km to Nautical Miles
        "avgSpeed": avgSpeed, #create the average of speed in the date (knots)
        "date": date
    }
    return distanceSpeed

def consumption(request, vessel, fleet):
    '''
    Controller that receives a request from the browser and two parameters in the url with the fleetId and vesselId
    returns a render page with the variables to use in the HTML
    '''
    try:
        ui, sessionId = validateSession(request.GET.get('SessionID'), LOGIN, appId, visualConf)
    except:
        return redirect(LOGIN)
    getData = "fleetId=" + fleet
    vesselsPosition = getXML(sessionId, getData, vsPos)
    #sees if in the request comes a POST to create a biger report and the range of the report
    if request.POST.get("dateone") and request.POST.get("datetwo"):
        dateOne = request.POST.get("dateone").replace("-", "")
        dateTwo = request.POST.get("datetwo").replace("-", "") + "23"
        dates = {
            "init": request.POST.get("dateone"),
            "final": request.POST.get("datetwo")
        }
        consumption = fuelUsage(vessel, dateOne, dateTwo)
    else:
        #if not, just the range of today until now
        dateOne =  datetime.datetime.today().isoformat().split("T")[0].replace("-", "")
        dateTwo =  (datetime.datetime.today().isoformat().split("T")[0].replace("-", "") + 
                    str((datetime.datetime.today() - datetime.timedelta(hours=1)).isoformat().split("T")[1][:2]))
        consumption = fuelUsage(vessel, dateOne, dateTwo)
        dates = {
            "init": datetime.datetime.today().isoformat().split("T")[0],
            "final": datetime.datetime.today().isoformat().split("T")[0]
        }
    visualConfig = ui
    vesselsNames = []
    #gets all the names and vesselsIds
    for v in vesselsPosition:
        var = {
            "name": v["vesselname"],
            "id": v["id"]
        }
        vesselsNames.append(var)
    bow = False #flag to render or not this column on the table and chart
    #looks up if the variables for bowthruster exists
    for c in consumption:
        if c["BOW902"] > 0 or c["BOW901"] > 0:
            bow = True
            break 
    vars = {"names": vesselsNames, "visual": visualConfig, "consumption": consumption, "vessel": vessel, 
            "fleetId": fleet, "bow": bow, "dates": dates, "session": sessionId}
    return render(request, "fuelReport.html", vars)

def fuelUsage(vi, dateOne, dateTwo):
    '''
    Function that receives a vesselId and a range of dates to create a report managing the logic 
    if already exists the range of dates that where asked for
    returns the totals of the day requested in a list
    '''
    conn = sql.connect(dbString)
    rows = selectRows(dateOne, dateTwo, vi, conn)#checks if the range exists
    if len(rows) == 0:
        #if not exists porceed to create the data of that range
        insertNewData(dateOne, dateTwo, vi, conn)
        rows = selectRows(dateOne, dateTwo, vi, conn) #now checks again for the range, now exists
        totals = createTotals(rows, dateOne, dateTwo) #create the totals of that range
    else:
        #if already exists just create the totals
        totals = createTotals(rows, dateOne, dateTwo)
    
    conn.close()

    return totals

def createTotals(rows, dateOne, dateTwo):
    '''
    Function that recieve the data of a range of dates in the params and process them to create 
    this day totals
    returns a list of dicts
    '''
    daysTotals = []
    #creates the datetimes for the range of dates strings in the params
    startDate = datetime.date(int(dateOne[:4]), int(dateOne[4:6]), int(dateOne[6:]))
    endDate = datetime.date(int(dateTwo[:4]), int(dateTwo[4:6]), int(dateTwo[6:8]))  
    #do...while create to loop through the range of dates  
    while True:

        metaData = []
        #gets all metadata strings from the rows selected
        for var in rows:
            metaData.append(var[0])
        metaData = sorted(set(metaData))#errase all the repeated matadata and sort them in order  
        #inicialice all datacodes
        dataCodes = {
            "PRP902": [],
            "PRP901": [],
            "PRS902": [],
            "PRS901": [],
            "BOW902": [],
            "BOW901": [],
            "GEP902": [],
            "GEP901": [],
            "GES902": [],
            "GES901": [],
        }
        dayString = startDate.isoformat().split("T")[0].replace("-", "")#make a string from the date without -
        #loops through all the rows selected to poblate the dataCodes with the values of the metadata of each day
        for tup in rows:
            if tup[2][:-2] == dayString:
                for meta in metaData:
                    if tup[0] == meta:
                        for k, v in dataCodes.iteritems():
                            if meta == k:
                                v.append(tup[1])#append to the dataCodes the respective data of each day in its metadata
            else:
                #if the day is already complete, pass it
                pass
        day = str(startDate.isoformat().split("T")[0])
        #creates the totals of each dataCode for this day
        totals = {
            "date": day,
            "PRP902": round(sum(dataCodes["PRP902"]), 2),
            "PRP901": round(sum(dataCodes["PRP901"]), 2),
            "PRS902": round(sum(dataCodes["PRS902"]), 2),
            "PRS901": round(sum(dataCodes["PRS901"]), 2),
            "BOW902": round(sum(dataCodes["BOW902"]), 2),
            "BOW901": round(sum(dataCodes["BOW901"]), 2),
            "GEP902": round(sum(dataCodes["GEP902"]), 2),
            "GEP901": round(sum(dataCodes["GEP901"]), 2),
            "GES902": round(sum(dataCodes["GES902"]), 2),
            "GES901": round(sum(dataCodes["GES901"]), 2),
            "total": round(sum(dataCodes["PRP902"]) + sum(dataCodes["PRS902"]) + 
                           sum(dataCodes["BOW902"]) + sum(dataCodes["GEP902"]) + sum(dataCodes["GES902"]), 2)
        }
        #if there is no data of any dataCode for this day, poblate with "No Data"
        if (totals["PRP902"] == 0 and totals["PRP901"] == 0 and totals["PRS902"] == 0 and totals["PRS901"] == 0 and 
            totals["BOW902"] == 0 and totals["BOW901"] == 0 and totals["GEP902"] == 0 and totals["GEP901"] == 0 and
            totals["GES902"] == 0 and totals["GES901"] == 0):
                totals = {
                    "date": day,
                    "PRP902": "No data",
                    "PRP901": "No data",
                    "PRS902": "No data",
                    "PRS901": "No data",
                    "BOW902": "No data",
                    "BOW901": "No data",
                    "GEP902": "No data",
                    "GEP901": "No data",
                    "GES902": "No data",
                    "GES901": "No data",
                    "total": "No data",
                }
                daysTotals.append(totals)
        else:
            #if the are data, append it to the list 
            daysTotals.append(totals)
        totals = {
            "date": "",
            "PRP902": 0,
            "PRP901": 0,
            "PRS902": 0,
            "PRS901": 0,
            "BOW902": 0,
            "BOW901": 0,
            "GEP902": 0,
            "GEP901": 0,
            "GES902": 0,
            "GES901": 0,
            "total": 0,
        }
        #stops the loop        
        if startDate == endDate:
            break
        startDate = startDate + datetime.timedelta(days=1)#increase date
    
    return daysTotals

def selectRows(dateOne, dateTwo, vi, conn):
    '''
    Function that receives a range of dates, a vesselId an a connection to the db to select the range
    returns a list of dicts
    '''
    date1 = datetime.date(int(dateOne[0:4]), int(dateOne[4:6]), int(dateOne[6:8]))
    date2 = datetime.date(int(dateTwo[0:4]), int(dateTwo[4:6]), int(dateTwo[6:8]))
    flags = []
    while date1 <= date2:
        rows1 = []
        dateTemp = date1.isoformat().split("T")[0].replace("-", "")
        cursor = conn.cursor()
        try:
            #selects all the data from the start date
            cursor.execute("""
		        select DataCode, DataValue from [3130-ETLFuelUsage] where DateString like '{0}%'
		        and vesselid = {1}
	        """.format(dateTemp, vi))
        except:
            print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
        rows1 = cursor.fetchall()
        cursor.close()
        if len(rows1) > 0:
            flags.append(1)
        else:
            flags.append(0)
        date1 += datetime.timedelta(days=1)
    #if there ara data in both dates, proceed to select all the date in that range
    if not(0 in flags):
        cursor = conn.cursor()
        try:
            #selects all the data in the range needed
            cursor.execute("""
                select DataCode, DataValue, DateString from [3130-ETLFuelUsage] where DateString <= '{0}' and DateString >= '{2}'
                and vesselid = {1}
            """.format(dateTwo, vi, dateOne))
        except:
            print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
    
        rows = cursor.fetchall()
        cursor.close()
    else:
        #if there is just one date, or none, return an empty list
        rows = []
    
    return rows

def insertNewData(dateOne, dateTwo, vi, conn):
    '''
    Function that receives a range of dates, a vesselId an a connection to the db to create the dataset for that range
    returns a list of dicts
    '''
    cursor = conn.cursor()
    try:
        #selects all metadata in the range given
        cursor.execute("""
			SELECT [DataCode], [DataValue], [TimeString], [vesselname] FROM [2160-DAQOnBoardData]
			where vesselid = {1}
			and DataCode in ('PRP001', 'PRP002', 'PRS001', 'PRS002', 
			'BOW001', 'BOW002', 'GEP001', 'GEP002', 'GES001', 'GES002')
			and TimeString >= '{0}' and TimeString <= '{2}'
			order by TimeString asc
		""".format(dateOne, vi, dateTwo))
    except:
        print "Error excecuting query to select [2160-DAQOnBoardData]", sys.exc_info()[0]
    rows = cursor.fetchall()
    cursor.close()
    hours = []
    if len(rows) == 0:
        return
    else:
        vesselName = rows[0][3]
    #iniciate all datacodes
    dataCodes = {
		"PRP001": [],
		"PRP002": [],
		"PRS001": [],
		"PRS002": [],
		"BOW001": [],
		"BOW002": [],
		"GEP001": [],
		"GEP002": [],
		"GES001": [],
		"GES002": [],
	}
    #loops to create the hours list of the day
    for data in rows:
        hours.append(data[2][:10])
    hours = sorted(set(hours))#sorted all the hours in order 
    consumptionHour = []
    #iniciates the dict of each hour
    consumption = {
		"date": "",
		"data": {}
	}
    #loops through the hours an for each hour append all the metadata of from it
    for date in hours:
        consumption["date"] = date
        for data in rows:#loops loking for each metadata
            if data[2][:10] == date:                				
                if data[0] == 'PRP001':
                    dataCodes["PRP001"].append(data[1])				
                elif data[0] == 'PRP002':
                    dataCodes["PRP002"].append(data[1])
                elif data[0] == 'PRS001':
                    dataCodes["PRS001"].append(data[1])
                elif data[0] == 'PRS002':
                    dataCodes["PRS002"].append(data[1])
                elif data[0] == 'BOW001':
                    dataCodes["BOW001"].append(data[1])
                elif data[0] == 'BOW002':
                    dataCodes["BOW002"].append(data[1])
                elif data[0] == 'GEP001':
                    dataCodes["GEP001"].append(data[1])
                elif data[0] == 'GEP002':
                    dataCodes["GEP002"].append(data[1])
                elif data[0] == 'GES001':
                    dataCodes["GES001"].append(data[1])		
                elif data[0] == 'GES002':
                    dataCodes["GES002"].append(data[1])
        consumption["data"] = dataCodes
        consumptionHour.append(consumption)#poblate the list with the inner dict
        dataCodes = {
			"PRP001": [],
			"PRP002": [],
			"PRS001": [],
			"PRS002": [],
			"BOW001": [],
			"BOW002": [],
			"GEP001": [],
			"GEP002": [],
			"GES001": [],
			"GES002": [],
		}
        consumption = {
			"date": "",
			"data": {}
		}
    #loops trhough the array created to create the totals of that hour for each metadata
    for hour in consumptionHour:
        date = ""
        totals = {}
        for k, v in hour.iteritems():#loops the dict, with key value to poblate the totals inner dict
            if k == "date":
                date = v
            if k == "data":
                dataHour = v
                totals = {
                    #if there is no data, poblate with 0, else do the math for the total of the hour
					"PRP902": 0 if len(dataHour["PRP002"]) == 0 else round((max(dataHour["PRP002"]) - min(dataHour["PRP002"])) * 0.2641720512415584, 4),#002 create the totals for fuel consupmtion in Galons from Liters
					"PRP901": 0 if len(dataHour["PRP001"]) == 0 else round((max(dataHour["PRP001"]) - min(dataHour["PRP001"])), 4),#001 create the totals for hours conusmption per hour 0.0 - 1.0
					"PRS902": 0 if len(dataHour["PRS002"]) == 0 else round((max(dataHour["PRS002"]) - min(dataHour["PRS002"])) * 0.2641720512415584, 4),
					"PRS901": 0 if len(dataHour["PRS001"]) == 0 else round((max(dataHour["PRS001"]) - min(dataHour["PRS001"])), 4),
					"BOW902": 0 if len(dataHour["BOW002"]) == 0 else round((max(dataHour["BOW002"]) - min(dataHour["BOW002"])) * 0.2641720512415584, 4),
					"BOW901": 0 if len(dataHour["BOW001"]) == 0 else round((max(dataHour["BOW001"]) - min(dataHour["BOW001"])), 4),
					"GEP902": 0 if len(dataHour["GEP002"]) == 0 else round((max(dataHour["GEP002"]) - min(dataHour["GEP002"])) * 0.2641720512415584, 4),
					"GEP901": 0 if len(dataHour["GEP001"]) == 0 else round((max(dataHour["GEP001"]) - min(dataHour["GEP001"])), 4),
					"GES902": 0 if len(dataHour["GES002"]) == 0 else round((max(dataHour["GES002"]) - min(dataHour["GES002"])) * 0.2641720512415584, 4),
					"GES901": 0 if len(dataHour["GES001"]) == 0 else round((max(dataHour["GES001"]) - min(dataHour["GES001"])), 4),
				}
            procDate = datetime.datetime.today().isoformat().split("T")
            procDate = "{0} {1}".format(procDate[0], procDate[1][:5])#creates the datestring for the db
            #loop to insert every hour data into the db
            for key, value in totals.iteritems():
                if str(value) == "0":#if empty, pass
                    pass
                else:
                    #selects if the metadata od the datestring excists for that vessel
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            SELECT * FROM [3130-ETLFuelUsage] where DataCode = '{0}' and DateString = '{1}' and vesselid = {2}
                        """.format(key, date, vi))
                    except:
                        print "Error excecuting query to select from [3130-ETLFuelUsage]", sys.exc_info()[0]
                    exists = cursor.fetchall()
                    cursor.close()
                    ##########################
                    if len(exists) == 0:#if the row don't exists, insert it
                        cursor = conn.cursor()
                        try:
                            cursor.execute("""
    							INSERT INTO [3130-ETLFuelUsage](procdate, vesselid, vesselname, DateString, DataCode, DataValue)
    							VALUES ('{0}', {1}, '{2}', '{3}', '{4}', {5})
    						""".format(procDate, vi, vesselName, date, key, value))
                        except:
                            print "Error excecuting query to insert into [3130-ETLFuelUsage]", sys.exc_info()[0]
                        cursor.commit()
                        cursor.close()                    
                    else:
                        pass
    print "Insert success"