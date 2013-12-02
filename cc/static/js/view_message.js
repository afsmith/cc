$(document).ready(function () {
    var page_timer = {},
            page_counter = {},
            i,
            timeout_id,
            tick,
            session_id = 0,
            incrementCounter,
            windowUnloadHandler,
            pageInitHandler;

    // init carousel
    $('#message_carousel').carousel({
        interval: false
    });

    // check if there is message_data to start tracking
    if (typeof message_data !== 'undefined') {

        // ----------------------------- Timer ----------------------------- //
        // init the page timer object
        for (i=0; i<message_data.page_count; i+=1) {
            page_timer[i+1] = 0;
            page_counter[i+1] = 0;
        }

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
        windowUnloadHandler = function () {
            var event_type = 'beforeunload';

            // window unload or pagehide => create tracking events
            if ('onpagehide' in window) {
                event_type = 'pagehide';
            }

            $(window).on(event_type, function () {
                $.ajax({
                    url: '/track/event/create/',
                    type: 'POST',
                    dataType: 'json',
                    async: false,
                    data: {
                        'type': 'EVENT',
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
                    session_id = resp.session;

                    windowUnloadHandler();
                } else {
                    console.log('ERROR: ' + resp.message);
                }
            });
        };

        // init page    
        pageInitHandler();
    
    } // end if message_data
    
}); // end document ready