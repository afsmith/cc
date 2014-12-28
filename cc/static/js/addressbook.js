/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, confirm*/
'use strict';

$(document).ready(function () {
    $('#delete_contact_button').on('click', function (e) {
        e.preventDefault();
        if (confirm('Are you sure you want to delete this contact?')) {
            $('#delete_contact_form').submit();
        }
    });


    // filter call list by date
    // $('#js_date_filter_message_list').change(function () {
    //     var days = $(this).val();

    //     $.ajax({
    //         url: '/report/message_list/',
    //         type: 'POST',
    //         data: {
    //             'days': days,
    //         },
    //     }).done(function (resp) {
    //         $('.messages_table > tbody').html(resp);
    //         $.bootstrapSortable();
    //     });
    // });
}); // end document ready
