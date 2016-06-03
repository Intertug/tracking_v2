from django.shortcuts import render
import pypyodbc as sql
from tracking.views import getVesselsPosition, visualConfiguration
from paths.views import getVesselGpsData
from tracking.settings import CONN_STRING as dbString
import datetime
import sys
import math
#from measurement.measures import Distance

def distance(request, vessel, fleet):
    sessionId = ""
    getData = "vesselid=" + vessel
    gpsData = getVesselGpsData(sessionId, getData)
    data = createDistance(gpsData["coordinates"])
    getData = "fleetId=" + fleet
    vesselsPosition = getVesselsPosition(sessionId, getData)
    vesselsNames = []
    for v in vesselsPosition:
        var = {
            "name": v["vesselname"],
            "id": v["id"]
        }
        vesselsNames.append(var)
    visualConfig = visualConfiguration("0")
    date = datetime.datetime.today().isoformat().split("T")[0].replace("-", "")
    vars = {"fleet": fleet, "distance": data["distance"], "speed": data["avgSpeed"], 
            "names": vesselsNames, "visual": visualConfig, "vessel": vessel, "date": date}
    return render(request, "distanceReport.html", vars)

def createDistance(coordinates):
    speeds = []
    distances = []
    radious = 6378
    for c in range(len(coordinates) - 1):
        lat1 = coordinates[c]["position"]["lat"]
        lon1 = coordinates[c]["position"]["lon"]
        lat2 = coordinates[c+1]["position"]["lat"]
        lon2 = coordinates[c+1]["position"]["lon"]
        a = math.cos(math.radians(90 - lat1)) * math.cos(math.radians(90 - lat2))
        b = math.sin(math.radians(90 - lat1)) * math.sin(math.radians(90 - lat2)) * math.cos(math.radians(lon1 - lon2)) 
        try:
            val = math.acos(a + b) * radious
        except:
            val = 0
        distances.append(val) 
        speeds.append(coordinates[c]["speed"])
    distanceSpeed = {
        "distance": round(sum(distances) * 0.539956803456, 2),
        "avgSpeed": round(sum(speeds) / len(speeds), 2)
    }
    return distanceSpeed

def consumption(request, vessel, fleet):
    sessionId = ""
    getData = "fleetId=" + fleet
    vesselsPosition = getVesselsPosition(sessionId, getData)
    if request.POST.get("dateone") and request.POST.get("datetwo"):
        dateOne = request.POST.get("dateone").replace("-", "")
        dateTwo = request.POST.get("datetwo").replace("-", "") + "23"
        consumption = fuelUsage(vessel, dateOne, dateTwo)
    else:
        dateOne =  datetime.datetime.today().isoformat().split("T")[0].replace("-", "")
        dateTwo =  (datetime.datetime.today().isoformat().split("T")[0].replace("-", "") + 
                    str((datetime.datetime.today() - datetime.timedelta(hours=1)).isoformat().split("T")[1][:2]))
        consumption = fuelUsage(vessel, dateOne, dateTwo)
    visualConfig = visualConfiguration("0")
    vesselsNames = []
    for v in vesselsPosition:
        var = {
            "name": v["vesselname"],
            "id": v["id"]
        }
        vesselsNames.append(var)
    bow = False
    for c in consumption:
        if c["BOW902"] > 0 or c["BOW901"] > 0:
            bow = True
            break 
    vars = {"names": vesselsNames, "visual": visualConfig, "consumption": consumption, "vessel": vessel, 
            "fleet": fleet, "bow": bow}
    return render(request, "fuelReport.html", vars)

def fuelUsage(vi, dateOne, dateTwo):
    
    conn = sql.connect(dbString)
    rows = selectRows(dateOne, dateTwo, vi, conn)
    if len(rows) == 0:
        insertNewData(dateOne, dateTwo, vi, conn)
        #rows = selectNewRows(dateOne, dateTwo, vi, conn)
        rows = selectRows(dateOne, dateTwo, vi, conn)
        totals = createTotals(rows, dateOne, dateTwo)
    else:
        #rows = selectNewRows(dateOne, dateTwo, vi, conn)
        totals = createTotals(rows, dateOne, dateTwo)
    
    conn.close()

    return totals

def createTotals(rows, dateOne, dateTwo):
    
    daysTotals = []
    startDate = datetime.date(int(dateOne[:4]), int(dateOne[4:6]), int(dateOne[6:]))
    endDate = datetime.date(int(dateTwo[:4]), int(dateTwo[4:6]), int(dateTwo[6:8]))  
    while True:

        metaData = []
        for var in rows:
            metaData.append(var[0])
        metaData = sorted(set(metaData))
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
        dayString = startDate.isoformat().split("T")[0].replace("-", "")
        for tup in rows:
            if tup[2][:-2] == dayString:
                for meta in metaData:
                    if tup[0] == meta:
                        for k, v in dataCodes.iteritems():
                            if meta == k:
                                v.append(tup[1])
            else:
                pass
        day = str(startDate.isoformat().split("T")[0])
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
        if startDate == endDate:
            break
        startDate = startDate + datetime.timedelta(days=1)
    
    return daysTotals

def selectRows(dateOne, dateTwo, vi, conn):

    cursor = conn.cursor()
    try:
        cursor.execute("""
		    select DataCode, DataValue from [3130-ETLFuelUsage] where DateString like '{0}%'
		    and vesselid = {1}
	    """.format(dateTwo[:-2], vi))
    except:
        print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
    
    rows1 = cursor.fetchall()
    cursor.close()
    #####################
    cursor = conn.cursor()
    try:
        cursor.execute("""
		    select DataCode, DataValue from [3130-ETLFuelUsage] where DateString like '{0}%'
		    and vesselid = {1}
	    """.format(dateOne, vi))
    except:
        print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
    
    rows2 = cursor.fetchall()
    cursor.close()

    if len(rows1) > 0 and len(rows2) > 0:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                select DataCode, DataValue, DateString from [3130-ETLFuelUsage] where DateString <= '{0}' and DateString >= '{2}'
                and vesselid = {1}
            """.format(dateTwo, vi, dateOne))
        except:
            print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
    
        rows = cursor.fetchall()
        cursor.close()
    else:
        rows = []
    
    return rows

def selectNewRows(dateOne, dateTwo, vi, conn):

    cursor = conn.cursor()
    try:
        cursor.execute("""
            select DataCode, DataValue, DateString from [3130-ETLFuelUsage] where DateString <= '{0}' and DateString >= '{2}'
            and vesselid = {1}
        """.format(dateTwo, vi, dateOne))
    except:
        print "Error excecuting query to select [3130-ETLFuelUsage]", sys.exc_info()[0]
    
    rows = cursor.fetchall()
    cursor.close()
    
    return rows

def insertNewData(dateOne, dateTwo, vi, conn):

    cursor = conn.cursor()
    try:
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
    for data in rows:
        hours.append(data[2][:10])
    hours = sorted(set(hours))
    consumptionHour = []
    consumption = {
		"date": "",
		"data": {}
	}
    for date in hours:
        consumption["date"] = date
        for data in rows:
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
        consumptionHour.append(consumption)
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
    for hour in consumptionHour:
        date = ""
        totals = {}
        for k, v in hour.iteritems():
            if k == "date":
                date = v
            if k == "data":
                dataHour = v
                totals = {
					"PRP902": 0 if len(dataHour["PRP002"]) == 0 else round((max(dataHour["PRP002"]) - min(dataHour["PRP002"])) * 0.2641720512415584, 4),
					"PRP901": 0 if len(dataHour["PRP001"]) == 0 else round((max(dataHour["PRP001"]) - min(dataHour["PRP001"])), 4),
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
            procDate = "{0} {1}".format(procDate[0], procDate[1][:5])
            for key, value in totals.iteritems():
                if str(value) == "0":
                    pass
                else:
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
                    if len(exists) == 0:
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