$(document).ready(function () {

    function createTrackingEvent(request_data) {
        $.ajax({
            url: '/track/event/create',
            type: 'POST',
            dataType: 'json',
            data: request_data
        }).done(function (resp) {
            console.log(resp);
        });
    }
    
    if (typeof message_data !== 'undefined') {
        createTrackingEvent($.extend({
            'type': 'SESSION'
        }, message_data));
    }


    // init carousel
    $('#message_carousel').carousel({
        interval: false
    });
}); // end document ready