// global variable
var lastIndex = 0,
    requestSent = false;

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
        if(!$el.hasClass("current")) {
            $el.addClass('hoveredRow');
        }
    }).on('mouseleave', 'tr', function(event) {
        $el = $(this);
        // change the color of selected row
        if(!$el.hasClass("current")) {
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
        if (!$el.hasClass("current")) {
            
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
            $el.removeClass("current");
        }
    });
});


