/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, Highcharts, CC_GLOBAL*/
'use strict';

$(document).ready(function () {
    var drawPieChart,
        tabClickHandler;

    // draw chart function
    drawPieChart = function (json_data) {
        var options,
            colors = Highcharts.getOptions().colors,
            len = json_data.values.length,
            column_colors = [],
            i = 0;

        if (typeof json_data === 'object' && len > 0) {
            // change color for key page
            for (i = 0; i < len; i += 1) {
                if (i === json_data.key_page - 1) {
                    column_colors.push(colors[3]);
                } else {
                    column_colors.push(colors[2]);
                }
            }

            // create option
            options = {
                chart: {
                    type: 'pie'
                },
                credits: {
                    enabled: false
                },
                title: {
                    text: json_data.subject,
                },
                plotOptions: {
                    pie: {
                        //allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            color: '#000000',
                            connectorColor: '#000000',
                            format: '<b>{key}</b>: {point.percentage: .1f} %'
                        },
                    }
                },
                tooltip: {
                    pointFormat: '{point.y:.1f} seconds - <b>{point.percentage:.1f}%</b>'
                },
                series: [{
                    showInLegend: false,
                    data: json_data.combo,
                }],
                exporting: {
                    enabled: false
                }
            };

            // draw chart
            $('#call_list_graph').highcharts(options);
            $('#call_list_detail').html('<p>Total pages: ' + len + '</p><p>Total visits: ' + json_data.total_visits + '</p>').removeClass('hidden');
        } else {
            $('#call_list_graph').html('<p class="alert alert-warning alert-block">This recipient didn\'t look at this file</p>');
            $('#call_list_detail').addClass('hidden');
        }
    };

    tabClickHandler = function (message_id, user_id, file_index) {
        $.ajax({
            url: '/report/dashboard/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': message_id,
                'recipient_id': user_id,
                'file_index': file_index
            }
        }).done(function (resp) {
            var i,
                html = '',
                html_partial = _.template(
                    '<li class="<%= data.li_class %>"><a href="#" data-toggle="tab" id="tab_<%= data.a_class %>"> \
                        <strong><%= data.name %></strong> \
                    </a></li>'
                );

            if (resp.status === 'OK') {
                for (i = 1; i <= resp.file_count; i += 1) {
                    html += html_partial({
                        li_class: i === parseInt(file_index, 10) ? 'active' : '',
                        a_class: [message_id, user_id, i].join('_'),
                        name: 'File ' + i, //resp.files[i - 1],
                        index: i
                    });
                }

                // render the nav
                $('#call_list_graph_nav').html(html).removeClass('hidden');

                // render the chart
                drawPieChart(resp.data);

                // render the detail button
                if (resp.data.total_visits !== 0) {
                    $('#detail_button').prop('href', function () {
                        return _.template(
                            '/report/<%= data.message_id %>/?user_id=<%= data.user_id %>&tab=<%= data.tab %>',
                            {message_id: message_id, user_id: user_id, tab: file_index}
                        );
                    }).removeClass('hidden');
                }
            }
        });
    };

    // click on each row
    $('.call_list_table').on('click', '.call_row', function () {
        var _this = $(this),
            this_row = _this.closest('tr');

        // reset state of right hand graph
        $('#call_list_graph_nav').addClass('hidden');
        $('#detail_button').addClass('hidden');
        $('#call_list_detail').addClass('hidden');

        // get graph for 1st file
        if (this_row.data('files') > 0) {
            tabClickHandler(this_row.data('message'), this_row.data('user'), 1);
        } else {
            $('#call_list_graph').html('<p class="alert alert-info">No Attachment</p>');
        }

        // handle css
        $('.call_row').removeClass('row_active');
        _this.addClass('row_active');

        return false;
    });

    // click on the tab nav on dashboard
    $('#call_list_graph_nav').on('click', 'a', function () {
        var this_id = $(this).prop('id'),
            id_arr = this_id.replace('tab_', '').split('_');

        tabClickHandler(id_arr[0], id_arr[1], id_arr[2]);
        return false;
    });

    // click on fix checkbox
    $('.js_fix').click(function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_email_cell = this_row.find('.email_cell'),
            old_email_val = this_email_cell.text();

        // change email cell to input
        this_email_cell.html('<input class="js_emailInput" type="text" value="' + old_email_val + '">');
        this_email_cell.data('old_value', old_email_val);
        this_row.find('.fix_cell').html('<button class="btn btn-default btn-small js_resend_button">Send</button>');

        return false;
    });

    // changing the text in email
    $('.bounces_table').on('keyup', '.js_emailInput', function () {
        $(this).closest('tr').find('.js_resend_button').addClass('btn-success');
    });

    // click on resend button
    $('.bounces_table').on('click', '.js_resend_button', function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_class = this_row.prop('class'),
            message_id = this_class.replace('message_', ''),
            new_email = this_row.find('.js_emailInput').val(),
            old_email = this_row.find('.email_cell').data('old_value');

        $.ajax({
            url: '/message/resend/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': message_id,
                'old_email': old_email,
                'new_email': new_email
            },
        }).done(function (resp) {
            if (resp.status === 'ERROR') {
                CC_GLOBAL.showErrorPopup(resp.message);
            } else {
                this_row.remove();
            }
        });

        return false;
    });

    // click on remove checkbox
    $('.js_remove').click(function () {
        $(this).closest('tr').find('.remove_cell').html('<button class="btn btn-default btn-small btn-danger js_removeButton">Remove</button>');
        return false;
    });

    $('.bounces_table').on('click', '.js_removeButton', function () {
        var this_row = $(this).closest('tr'),
            this_id = this_row.prop('id').replace('row_', '');

        $.ajax({
            url: '/report/remove_bounce/' + this_id + '/',
            type: 'POST',
            dataType: 'json',
        }).done(function () {
            this_row.remove();
        });

        return false;
    });

    // search call list table
    CC_GLOBAL.filterTable('.call_list_table > tbody', '#js_search_email');

    // filter call list by date
    $('#js_date_filter_call_list').change(function () {
        var days = $(this).val();

        $.ajax({
            url: '/report/call_list/',
            type: 'POST',
            data: {
                'days': days,
            },
        }).done(function (resp) {
            $('.call_list_table > tbody').html(resp);
            $.bootstrapSortable();
        });
    });

    // search call list table
    CC_GLOBAL.filterTable('.messages_table > tbody', '#js_search_message');

    // filter call list by date
    $('#js_date_filter_message_list').change(function () {
        var days = $(this).val();

        $.ajax({
            url: '/report/message_list/',
            type: 'POST',
            data: {
                'days': days,
            },
        }).done(function (resp) {
            $('.messages_table > tbody').html(resp);
            $.bootstrapSortable();
        });
    });

}); // end document ready