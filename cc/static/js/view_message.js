$(document).ready(function () {
    var page_timer = {},
        page_counter = {},
        i,
        timeout_id,
        tick,
        incrementCounter,
        windowUnloadHandler,
        windowPageShowHandler,
        pageInitHandler,
        initTimerCounter,
        createEventAjax,
        pageChangeHandler,
        safariHandler;

    // init carousel
    $('#message_carousel').carousel({
        interval: false
    });

    // check if there is message_data to start tracking
    if (typeof message_data !== 'undefined') {

        // ----------------------------- Timer ----------------------------- //
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

        pageChangeHandler = function () {
            // get current active page
            var active_page = $('#message_carousel .active').index() + 1;

            // init timer and counter for page 1
            tick(active_page);
            incrementCounter(active_page);
        };

        initTimerCounter = function (message_data) {
            // init the page timer object
            for (i=0; i<message_data.page_count; i+=1) {
                page_timer[i+1] = 0;
                page_counter[i+1] = 0;
            }

            pageChangeHandler();
        };

        initTimerCounter(message_data);
        


        // ----------------------------- Carousel ----------------------------- //
        $('#message_carousel').on('slid', function () {
            pageChangeHandler();
        });


        // ----------------------------- Tracking ----------------------------- //
        createTrackingEventAjax = function (event_type, session_id) {
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
        };

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
                createTrackingEventAjax(event_type, session_id);
            });
        };

        safariHandler = function (session_id) {
            interval_id = setInterval(function () {
                createTrackingEventAjax('safari_interval', session_id)
            }, 500);
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
                        is_iOS = resp.is_iOS,
                        is_safari = (navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1);

                    // check if this is Safari on desktop
                    if (is_safari && !is_iOS) {
                        safariHandler(session_id);
                    } else {
                        windowUnloadHandler(session_id, is_iOS);    
                    }
                } else {
                    console.log('ERROR: ' + resp.message);
                }
            });
        };

        // init page    
        pageInitHandler();
    
    } // end if message_data
    
}); // end document ready