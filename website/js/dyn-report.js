// global variable
var lastIndex = 0;

$(function() {

    // set up variables
    var $el,
        $message = $("div#message"),
        $content = $("div#content"),
        $resultTable = $("table#resultTable"),
        $prevSelectedRow;

    // table settings
    /* For cell text alignment */
    $("table td:first-child, table th:first-child").addClass("first");
    /* For removing the last border */
    $("table td:last-child, table th:last-child").addClass("last");

    // highlighting hovered row
    $resultTable.on('mouseenter', 'tr', function(event) {
        $el = $(this);
        // change the color of selected row
        if(!$el.hasClass("current") && !$el.hasClass("alarm")) {
            $el.addClass('hoveredRow');
        }
    }).on('mouseleave', 'tr', function(event) {
        $el = $(this);
        // change the color of selected row
        if(!$el.hasClass("current") && !$el.hasClass("alarm")) {
            $el.removeClass('hoveredRow');
            $el.css('background', '-moz-linear-gradient(100% 25% 90deg, #fefefe, #f9f9f9)');
            $el.css('background', '-webkit-gradient(linear, 0% 0%, 0% 25%, from(#f9f9f9), to(#fefefe))');
        }
    });

    // clicking on row does stuff
    $resultTable.delegate("tr", "click", function() {
        // cache this, as always, is good form
        $el = $(this);
        
        // if this is already the active cell, remove current class
        if(!$el.hasClass("current") && !$el.hasClass("alarm")) {
            
            // make sure the correct column is current
            $("table#resultTable tr").removeClass("current");
            $el.addClass("current");

            // change the color of selected row
            $el.addClass('hoveredRow');
            if($prevSelectedRow) {
                $prevSelectedRow.removeClass('hoveredRow');
            }
            $prevSelectedRow = $el;
        } else {
            $("table#resultTable tr").removeClass("current");
        }
    });

    // hide result table
    $resultTable.hide();

    // get summary report by AJAX
    sendAJAX();

    // show result table
    if (!$resultTable.is(":visible"))
        $resultTable.fadeIn(250);
});

function sendAJAX() {
    var $el,
        $resultTable = $("table#resultTable");

    $.ajax({
        async: true,
        cache: false,
        type: 'GET',
        url: '/data',
        contentType: 'application/json; charset=UTF-8',
        dataType: "json",
        success: function(data) {
            var resultObj = data.result;
            var errObj = data.error;

            try { 
                if(resultObj !== undefined) {
                    // for each site result
                    $.each(resultObj, function(index, dataObj) {
                        var hostname = dataObj.hostname;
                        var ip = dataObj.ip;
                        var ssh_port = dataObj.ssh_port;
                        var update_time = dataObj.update_time;
                        var alarm = dataObj.alarm;

                        var newRowStr = "";
                        if(!alarm)
                            newRowStr = "<tr> \
                                            <td>" + (lastIndex + 1) + "</td> \
                                            <td class=\"hostname\">" + hostname + "</td> \
                                            <td class=\"ipaddr\">" + ip + "</td> \
                                            <td class=\"numbers\">" + ssh_port + "</td> \
                                            <td class=\"numbers\">" + update_time + "</td> \
                                         </tr>";
                        else
                            newRowStr = "<tr class=\"alarm\"> \
                                            <td>" + (lastIndex + 1) + "</td> \
                                            <td class=\"hostname\">" + hostname + "</td> \
                                            <td class=\"ipaddr\">" + ip + "</td> \
                                            <td class=\"numbers\">" + ssh_port + "</td> \
                                            <td class=\"numbers\">" + update_time + "</td> \
                                         </tr>";

                        $resultTable.append(newRowStr);

                        lastIndex++;
                    }); // end of site array loop
                }
            } catch(err) {
                var vDebug = "";
                for (var prop in err) { 
                   vDebug += "property: "+ prop+ " value: ["+ err[prop]+ "]\n";
                }
                vDebug += "toString(): " + " value: [" + err.toString() + "]";

                console.log(vDebug);
            }
        }
    });
}
