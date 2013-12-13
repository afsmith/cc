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
        var chart_data,
            options,
            chart;

        if (typeof json_data === 'object' && json_data.values.length > 0) {
            log(json_data);
 
            chart_data = [{
                data: json_data.values,
                bars: {
                    show: true,
                    barWidth: 0.5,
                    align: 'center',
                    //lineWidth: 1,
                    showNumbers: true,
                    numbers : {
                        xAlign: function(x) { return x; },
                        yAlign: function(y) { return y + 0.35; },
                    },
                },
                highlightColor: '#AA4643',
                color: '#AA4643'
            }];

            options = {
                title: 'Page graph',
                xaxis: {
                    axisLabel: 'Page',
                    axisLabelUseCanvas: true,
                    ticks: json_data.labels,
                },
                yaxis: {
                    axisLabel: 'Total time',
                    axisLabelUseCanvas: true,
                },
                grid: {
                    //hoverable: true,
                    //clickable: false,
                    //borderWidth: 1
                },
                legend: {
                    show: true,
                    labelBoxBorderColor: "none",
                    position: "right"
                },
            };

            // draw chart and highlight the key page
            $.plot($("#report_graph"), chart_data, options).highlight(0, json_data.key_page-1); // [0] = series 0, [1] = index of the column
        } else {
            log('No data to display');
        }
    };

    // fetch data from backend and draw column chart
    initDrawChart = function () {
        $.ajax({
            url: '/report/summary/',
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
                    var i = 0,
                        html = '',
                        iOS_class = '';

                    if (resp.length) {
                        for (i; i < resp.length; i+=1) {
                            /*iOS_class = ''
                            if ($.inArray(resp[i].device, ['iPhone', 'iPod', 'iPad']) > -1) {
                                iOS_class = ' row_iOS';
                            }*/
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
            url: '/report/session/',
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

    /*$('.report_table').tooltip({
        selector: '.row_iOS',
        title: "iOS browser likes to hold on the it's events so we couldn't collect the tracking data. We are working on a way to fix this."
    });*/
}); // end document ready