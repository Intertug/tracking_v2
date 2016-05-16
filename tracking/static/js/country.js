$("ul#rm-list li a").click(function (event) {
    $(".panel-primary").addClass("hidden");
    id = String($(this).attr("id"))
    link = "#table-" + id
    event.preventDefault(event);
    $(link).toggleClass("hidden");
    for (var i = 0; i < markers.length; i++) {
        if (slugify(markers[i]["title"]) === id){
            map.setCenter(markers[i]["position"])
            map.setZoom(12)
        }
    }
})

function slugify(text) {
    return text.toString().toLowerCase()
      .replace(/\s+/g, '-')           // Replace spaces with -
      .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
      .replace(/\-\-+/g, '-')         // Replace multiple - with single -
      .replace(/^-+/, '')             // Trim - from start of text
      .replace(/-+$/, '');            // Trim - from end of text
}