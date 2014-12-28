/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, confirm, indexOf*/
'use strict';

$(document).ready(function () {
    $('#delete_contact_button').on('click', function (e) {
        e.preventDefault();
        if (confirm('Are you sure you want to delete this contact?')) {
            $('#delete_contact_form').submit();
        }
    });

    $('#contacts_table th').on('click', function (e) {
        e.preventDefault();
        var sort_by = $(e.target).prop('id').replace('sort_', ''),
            current = CC_GLOBAL.GETParam.sort || '',
            sort = '?sort=',
            query_str = window.location.search;

        if (current.indexOf(sort_by) > -1) {
            sort += current.replace(sort_by + ',', '');
        } else {
            sort += current + sort_by + ',';
        }

        query_str = (CC_GLOBAL.GETParam.sort === undefined)
            ? query_str + sort
            : query_str.replace('?sort=' + current, sort);
        window.location = window.location.pathname + query_str;
    });
}); // end document ready
