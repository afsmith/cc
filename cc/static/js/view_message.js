$(document).ready(function () {
    var page_timer = {},
        page_counter = {},
        i,
        timeout_id,

        // function
        incrementTimer,
        incrementCounter,
        windowUnloadHandler,
        windowPageShowHandler,
        pageInitHandler,
        initTimerCounter,
        createEventAjax,
        pageChangeHandler,
        safariHandler;

    // check if there is global var message_data to start tracking
    if (typeof CC_GLOBAL.message_data !== 'undefined') {
        // document is ready inside flexpaper viewer
        $(window).on('onDocumentLoaded', function () {
            var flex_viewer = $FlexPaper('message_viewer');


            // ----------------------------- Timer ----------------------------- //
            
            // main timer function runs every 100ms
            incrementTimer = function (page_number) {
                page_timer[page_number] += 1;
                clearTimeout(timeout_id);
                timeout_id = setTimeout(function() {
                    incrementTimer(page_number);
                }, 100);
            };

            // function to handle page counter
            incrementCounter = function (page_number) {
                page_counter[page_number] += 1;
            };

            pageChangeHandler = function (page_number) {
                // init timer and counter for page 1
                incrementTimer(page_number);
                incrementCounter(page_number);    
            };

            initTimerCounter = function (message_data) {
                // init the page timer object
                for (i=0; i<message_data.page_count; i+=1) {
                    page_timer[i+1] = 0;
                    page_counter[i+1] = 0;
                }
            };

            initTimerCounter(CC_GLOBAL.message_data);

            // handle page change event
            $(window).on('onCurrentPageChanged', function (e, page_number) {
                console.log('Page changed: ' +  page_number);

                pageChangeHandler(page_number);
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
                    initTimerCounter(CC_GLOBAL.message_data);
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
                    data: $.extend({'type': 'SESSION'}, CC_GLOBAL.message_data)
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
                        log('ERROR: ' + resp.message);
                    }
                });
            };

            // init page
            pageInitHandler();
    
        // ----------------------------- END ----------------------------- //
        }); // end onDocumentLoaded 
    } // end if CC_GLOBAL.message_data
}); // end document ready