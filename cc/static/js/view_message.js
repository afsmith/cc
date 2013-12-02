$(document).ready(function () {
    var page_timer = {},
        page_counter = {},
        i,
        timeout_id,
        tick,
        //session_id = 0,
        incrementCounter,
        windowUnloadHandler,
        pageInitHandler,
        initTimerCounter;

    // init carousel
    $('#message_carousel').carousel({
        interval: false
    });

    initTimerCounter = function(message_data) {
        // init the page timer object
        for (i=0; i<message_data.page_count; i+=1) {
            page_timer[i+1] = 0;
            page_counter[i+1] = 0;
        }
    };

    // check if there is message_data to start tracking
    if (typeof message_data !== 'undefined') {

        // ----------------------------- Timer ----------------------------- //
        initTimerCounter(message_data);

        // function to handle page counter
        incrementCounter = function (page_number) {
            page_counter[page_number] += 1;
        };

        // main timer function runs every 100ms
        tick = function (page_number) {
            page_timer[page_number] += 1;
            clearTimeout(timeout_id);
            timeout_id = setTimeout(function() {
                tick(page_number);
            }, 100);
        };

        // init timer and counter for page 1
        tick(1);
        incrementCounter(1);


        // ----------------------------- Carousel ----------------------------- //
        $('#message_carousel').on('slid', function () {
            // get the page number and run tick() to count time for that page
            var page_number = $(this).find('.active').index() + 1;
            tick(page_number);

            // and increment the counter
            incrementCounter(page_number);
        });


        // ----------------------------- Tracking ----------------------------- //
        windowPageShowHandler = function () {
            $(window).on('pageshow', function () {
                initTimerCounter(message_data);
            });
        };

        windowUnloadHandler = function (session_id, is_iOS) {
            var event_type = 'beforeunload';

            // if the device is iOS then use pagehide event instead since iOS doesn't support beforeunload event
            if (is_iOS) {
                event_type = 'pagehide';

                // bind pageshow event
                windowPageShowHandler();
            }

            $(window).on(event_type, function () {
                $.ajax({
                    url: '/track/event/create/',
                    type: 'POST',
                    dataType: 'json',
                    async: false,
                    data: {
                        'type': 'EVENT',
                        'js_event_type': event_type,
                        'timer': page_timer,
                        'counter': page_counter,
                        'session_id': session_id,
                    }
                });
            });
        };

        pageInitHandler = function () {
            // init page => create tracking session
            $.ajax({
                url: '/track/event/create/',
                type: 'POST',
                dataType: 'json',
                data: $.extend({'type': 'SESSION'}, message_data)
            }).done(function (resp) {
                if (resp.status === 'OK') {
                    var session_id = resp.session_id,
                        is_iOS = resp.is_iOS;

                    windowUnloadHandler(session_id, is_iOS);
                } else {
                    console.log('ERROR: ' + resp.message);
                }
            });
        };

        // init page    
        pageInitHandler();
    
    } // end if message_data
    
}); // end document ready