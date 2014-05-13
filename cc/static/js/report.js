/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, CC_GLOBAL, log, i18, Highcharts*/
'use strict';

$(document).ready(function () {
    var _drawBarChart,
        initDrawChart,
        this_message_id = $('#js_selectMessage').val();

    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // draw chart function
    _drawBarChart = function (json_data) {
        var options,
            colors = Highcharts.getOptions().colors,
            len = json_data.values.length,
            column_colors = [],
            bar_width = Math.log(39 / len) * 80, // HIEU's algorithm to set column width nicely
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
                    type: 'column'
                },
                credits: {
                    enabled: false
                },
                title: {
                    text: json_data.subject,
                },
                subtitle: {
                    //text: 'Subject: '
                },
                xAxis: {
                    categories: json_data.labels,
                    labels: {
                        formatter: function () {
                            return this.value[1];
                        }
                    }
                },
                yAxis: {
                    title: {
                        text: 'Total time spent (seconds)'
                    }
                },
                plotOptions: {
                    column: {
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            color: '#000000',
                            style: {
                                fontWeight: 'bold'
                            },
                            formatter: function () {
                                return this.y + ' s';
                            }
                        },
                        colorByPoint: true,
                    }
                },
                colors: column_colors,
                tooltip: {
                    formatter: function () {
                        return this.x[1] + ': ' + this.y + ' seconds';
                    }
                },
                series: [{
                    showInLegend: false,
                    data: json_data.values,
                    pointWidth: bar_width,
                }]
            };

            // draw chart
            $('.report_graph').highcharts(options);
        } else {
            log('No data to display');
        }
    };

    // fetch data from backend and draw column chart
    initDrawChart = function () {
        $.ajax({
            url: '/report/drilldown/',
            type: 'POST',
            dataType: 'json',
            data: {'message_id': this_message_id},
        }).done(function (resp) {
            _drawBarChart(resp);
        });
    };
    // display the chart on page init
    initDrawChart();

    // close the deal when click checkbox
    $('.js_sold').click(function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            action = _this.prop('checked') ? 'create' : 'remove',
            id_pair = this_id.replace('row_', '').split('_'),
            message_id = id_pair[0],
            user_id = id_pair[1];

        $.ajax({
            url: '/track/close_deal/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': message_id,
                'user_id': user_id,
                'action': action
            }
        }).done(function (resp) {
            // make the row lighter
            if (resp.status === 'OK') {
                if (action === 'create') {
                    this_row.addClass('sold');
                } else {
                    this_row.removeClass('sold');
                }
            }
        });
    });

    // click on email address cell
    $('.cell_email').click(function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            id_pair = this_id.replace('row_', '').split('_'),
            message_id = id_pair[0],
            user_id = id_pair[1],
            all_log_rows = $('.js_log_' + this_id);

        // if the log rows are shown
        if (this_row.hasClass('log_opened')) {
            // hide the log rows and remove the blue background
            all_log_rows.hide();
            this_row.removeClass('log_opened');
        } else {
            // add blue background
            this_row.addClass('log_opened');

            // show the logs or fetch it with ajax
            if (all_log_rows.length) {
                all_log_rows.show();
            } else {
                $.ajax({
                    url: '/report/user/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'message_id': message_id,
                        'user_id': user_id,
                    }
                }).done(function (resp) {
                    var i,
                        html = '',
                        iOS_class = '';

                    if (resp.length) {
                        for (i = 0; i < resp.length; i += 1) {
                            html += [
                                '<tr id="js_session_' + resp[i].id + '" class="log_row js_log_' + this_id + iOS_class + '">',
                                '<td></td>',
                                '<td>' + resp[i].created_ts + '</td>',
                                '<td></td>',
                                '<td>' + resp[i].total_time + '</td>',
                                '<td></td>',
                                '<td>' + resp[i].client_ip + '</td>',
                                '<td>' + resp[i].device + '</td>',
                                '</tr>'
                            ].join('');
                        }
                    }
                    this_row.after(html);
                });
            }
        }
    });

    // draw the chart again for each session after click on each session log row
    $('.report_table').on('click', '.log_row', function () {
        var this_session_id = $(this).prop('id').replace('js_session_', '');
        $.ajax({
            url: '/report/drilldown/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': this_message_id,
                'session_id': this_session_id
            },
        }).done(function (resp) {
            _drawBarChart(resp);
        });
    });

    // tooltip on row with no tracking data
/*    $('.report_table').tooltip({
        selector: '.no_tracking_data',
        title: "This user hasn't looked at your message yet."
    });
*/

    // click on resend button
    $('.js_resend').click(function () {
        $(this).parent().html('<button class="btn btn-default btn-small js_resendButton">Send</button>');
    });

    $('.report_table').on('click', '.js_resendButton', function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            id_pair = this_id.replace('row_', '').split('_'),
            message_id = id_pair[0],
            user_id = id_pair[1];

        $.ajax({
            url: '/message/resend/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': message_id,
                'user_id': user_id
            },
        }).done(function (resp) {
            if (resp.status === 'ERROR') {
                CC_GLOBAL.showErrorPopup(resp.message);
            }
            _this.remove();
        });
    });

    // if there is ?user in GET query then click on it and scroll down a bit
    if (CC_GLOBAL.GETParam.user !== undefined) {
        $('#user_' + CC_GLOBAL.GETParam.user).trigger('click');
        $(window).delay(500).scrollTop(600);
    }
}); // end document ready