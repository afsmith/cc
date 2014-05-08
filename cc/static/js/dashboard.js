/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, Highcharts, CC_GLOBAL*/
'use strict';

$(document).ready(function () {
    var _drawPieChart;

    // draw chart function
    _drawPieChart = function (json_data) {
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
            $('#class_list_detail').html('<p>Total pages: ' + len + '</p><p>Total visits: ' + json_data.total_visits + '</p>');
        } else {
            $('#call_list_graph').html('<p class="alert alert-block">This recipient didn\'t look at your offer</p>');
            $('#class_list_detail').html('');
        }
    };

    // click on each row
    $('.call_list_table').on('click', '.call_row', function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            id_pair = this_id.replace('row_', '').split('_'),
            message_id = id_pair[0],
            user_id = id_pair[1];

        $.ajax({
            url: '/report/drilldown/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': message_id,
                'recipient_id': user_id
            },
        }).done(function (resp) {
            $('.call_row').removeClass('row_active');
            _this.addClass('row_active');
            _drawPieChart(resp);

            // add detail button
            $('#detail_button').prop('href', function () {
                return '/report/' + message_id + '/?user=' + user_id;
            }).removeClass('hidden');
        });
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
        this_row.find('.fix_cell').html('<button class="btn btn-default btn-small js_resendButton">Send</button>');
    });

    // changing the text in email
    $('.bounces_table').on('keyup', '.js_emailInput', function () {
        $(this).closest('tr').find('.js_resendButton').addClass('btn-success');
    });

    // click on resend button
    $('.bounces_table').on('click', '.js_resendButton', function () {
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
    });

    // click on remove checkbox
    $('.js_remove').click(function () {
        $(this).closest('tr').find('.remove_cell').html('<button class="btn btn-default btn-small btn-danger js_removeButton">Remove</button>');
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
    });

    // search call list table
    CC_GLOBAL.filterTable('.call_list_table > tbody', '#js_search_email');

    // filter call list by date
    $('#js_date_filter').change(function () {
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

}); // end document ready