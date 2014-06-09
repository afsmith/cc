/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log, $FlexPaper*/
'use strict';

$(document).ready(function () {
    var page_timer = {},
        page_counter = {},
        i,
        timeout_id,
        pagechange_interval_id,
        is_iOS = false,
        is_Android = false,
        current_page = 0,

        // function
        incrementTimer,
        incrementCounter,
        windowUnloadHandler,
        windowPageShowHandler,
        pageInitHandler,
        initTimerCounter,
        pageChangeHandler,
        safariOrMobileHandler,
        createTrackingEventAjax;


    // document is ready inside flexpaper viewer
    $(window).on('onDocumentLoaded', function () {
        var flex_viewer = $FlexPaper('message_viewer');

        // check if there is global var message_data to start tracking
        if (CC_GLOBAL.message_data !== undefined) {

            // ----------------------------- Timer ----------------------------- //

            // main timer function runs every 100ms
            incrementTimer = function (page_number) {
                page_timer[page_number] += 1;
                clearTimeout(timeout_id);
                timeout_id = setTimeout(function () {
                    incrementTimer(page_number);
                }, 100);
            };

            // function to handle page counter
            incrementCounter = function (page_number) {
                page_counter[page_number] += 1;
            };

            initTimerCounter = function (message_data) {
                // init the page timer object
                for (i = 0; i < message_data.page_count; i += 1) {
                    page_timer[i + 1] = 0;
                    page_counter[i + 1] = 0;
                }
            };

            initTimerCounter(CC_GLOBAL.message_data);

            // handle the page change event
            // TODO: check when onCurrentPageChanged is supported in iOS or Android
            pageChangeHandler = function () {
                if (is_iOS || is_Android) {

                    clearInterval(pagechange_interval_id);
                    pagechange_interval_id = setInterval(function () {
                        if (flex_viewer.getCurrPage() !== current_page) {
                            incrementCounter(flex_viewer.getCurrPage());
                        }

                        current_page = flex_viewer.getCurrPage();
                        page_timer[current_page] += 1;
                    }, 100);

                } else {
                    $(window).on('onCurrentPageChanged', function (e, page_number) {
                        incrementTimer(page_number);
                        incrementCounter(page_number);
                    });
                }
            };


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
                    current_page = 0;
                    pageChangeHandler();
                });
            };

            windowUnloadHandler = function (session_id) {
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

            safariOrMobileHandler = function (session_id) {
                setInterval(function () {
                    createTrackingEventAjax('safari_interval', session_id);
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
                            is_safari = (navigator.userAgent.indexOf('Safari') !== -1 && navigator.userAgent.indexOf('Chrome') === -1);
                        is_iOS = resp.is_iOS;
                        is_Android = resp.is_Android;

                        log(resp.device);

                        // init page change handler after getting is_iOS
                        pageChangeHandler();

                        // check if this is Safari on desktop
                        if ((is_safari && !is_iOS) || is_Android) {
                            safariOrMobileHandler(session_id);
                        } else {
                            windowUnloadHandler(session_id);
                        }
                    } else {
                        log('ERROR: ' + resp.message);
                    }
                });
            };

            // init page
            pageInitHandler();

        // ----------------------------- END ----------------------------- //
        }  // end if CC_GLOBAL.message_data

        // init download button
        if (!_.isUndefined(CC_GLOBAL.download_url)) {
            $('.js_download_button').click(function () {
                if (_.isUndefined(CC_GLOBAL.message_data)) {
                    window.location = CC_GLOBAL.download_url;
                } else {
                    window.location = _.template('<%= data.url %>?user=<%= data.user %>&message=<%= data.message %>', {
                        url: CC_GLOBAL.download_url,
                        user: CC_GLOBAL.message_data.user_id,
                        message: CC_GLOBAL.message_data.message_id,
                    });
                }
            }).show();
        }
    }); // end onDocumentLoaded 
}); // end document ready