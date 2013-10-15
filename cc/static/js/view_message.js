$(document).ready(function () {

    // ----------------------------- Timer ----------------------------- //
    var page_timer = {},
        i,
        timeout_id,
        tick,
        session_id = 0,
        windowUnloadHandler,
        pageInitHandler;

    // init the page timer object
    for (i=0; i<message_data.page_count; ++i) {
        page_timer[i+1] = 0;
    }

    // main timer function runs every 100ms
    tick = function (page_number) {
        page_timer[page_number] += 1;
        clearTimeout(timeout_id);
        timeout_id = setTimeout(function() {
            tick(page_number);
        }, 100);
    };

    // init tick for page 1
    tick(1);


    // ----------------------------- Carousel ----------------------------- //
    $('#message_carousel').carousel({
        interval: false
    }).on('slid', function () {
        // get the page number and run tick() to count time for that page
        var page_number = $(this).find('.active').index() + 1;
        tick(page_number);
    });


    // ----------------------------- Tracking ----------------------------- //
    windowUnloadHandler = function () {
        // window unload => create tracking events
        $(window).unload(function () {
            $.ajax({
                url: '/track/event/create',
                type: 'POST',
                dataType: 'json',
                async: false,
                data: {
                    'type': 'EVENT',
                    'timer': page_timer,
                    'session_id': session_id
                }
            }).done(function (resp) {
                console.log(resp);
            });
        });
    };

    pageInitHandler = function () {
        // init page => create tracking session
        $.ajax({
            url: '/track/event/create',
            type: 'POST',
            dataType: 'json',
            data: $.extend({'type': 'SESSION'}, message_data)
        }).done(function (resp) {
            if (resp.status === 'OK') {
                session_id = resp.session;

                windowUnloadHandler();
            } else {
                console.log('ERROR: ' + resp.message);
            }
        });
    };

    
    if (typeof message_data !== 'undefined') {
        pageInitHandler();
    }
    
}); // end document ready