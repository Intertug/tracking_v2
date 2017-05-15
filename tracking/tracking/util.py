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