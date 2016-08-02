rowsGpsDate = $(".gpsdate")
rowsRpmDate = $(".rpmdate")

redAlertDates(rowsGpsDate)
redAlertDates(rowsRpmDate)

function redAlertDates(array) {
    for (var row = 0; row < array.length; row++) {
        year = array[row]["innerText"].slice(0, 4)
        month = array[row]["innerText"].slice(5, 7)
        day = array[row]["innerText"].slice(8, 10)
        hours = array[row]["innerText"].slice(11, 13)
        minutes = array[row]["innerText"].slice(14, 16)
        seconds = array[row]["innerText"].slice(17, 19)
        gpsDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), parseInt(hours), parseInt(minutes), parseInt(seconds))
        today = new Date()
        if ((today - gpsDate) < 36e5) {

        }
        else{
            array[row]["attributes"][0]["nodeValue"] = "danger"
        }
    }
}

