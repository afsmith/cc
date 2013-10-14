$(document).ready(function () {

    function createTrackingEvent(request_data) {
        $.ajax({
            url: '/track/event/create',
            type: 'POST',
            dataType: 'json',
            async: false, // to be finished before window unload
            data: request_data
        }).done(function (resp) {
            console.log(resp);
        });
    }
    
    // create tracking session when first load the page
    if (typeof message_data !== 'undefined') {
        /*createTrackingEvent($.extend({
            'type': 'SESSION'
        }, message_data));*/
    }


    // ----------------------------- Timer ----------------------------- //
    var page_timer = {},
        i,
        timeout_id;

    // init the page timer object
    for (i=0; i<message_data.page_count; ++i) {
        page_timer[i+1] = 0;
    }

    // main timer function runs every 50ms
    function tick(page_number) {
        page_timer[page_number] += 0.5;
        clearTimeout(timeout_id);
        timeout_id = setTimeout(function() {
            tick(page_number);
        }, 50);
    }

    // init tick for page 1
    tick(1);
    // ----------------------------- Timer ----------------------------- //

    // init carousel
    $('#message_carousel').carousel({
        interval: false
    }).on('slid', function () {
        // get the page number and run tick() to count time for that page
        var page_number = $(this).find('.active').index() + 1;
        tick(page_number);
    });

    $(window).unload(function () {
        createTrackingEvent($.extend({
            'type': 'EVENT',
            'timer': page_timer
        }, message_data));
    });
}); // end document ready