$(document).ready(function () {
    var _drawChart,
        initDrawChart,
        this_message_id = $('#js_selectMessage').val();

    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // draw chart function
    _drawChart = function (json_data) {
        var data,
            options,
            chart;

        if (json_data.length > 0) {
            data = new google.visualization.DataTable();
            data.addColumn({type: 'string', label: 'Page'});
            data.addColumn({type: 'number', label: 'Total time'});
            data.addColumn({type: 'string', role: 'annotation'});
            data.addRows(json_data);

            options = {
                title: 'Page graph',
                hAxis: {
                    gridlines: {
                        count: json_data.length
                    }
                },
                vAxis: {
                    format: '#s'
                },
                series: {
                    0: {
                        type: 'bars'
                    },
                    1: {
                        type: 'line',
                        //color: 'grey', 
                        lineWidth: 0,
                        pointSize: 0,
                        visibleInLegend: false
                    }
                },
                height: 500
            };

            var view = new google.visualization.DataView(data);
            view.setColumns([0, 1, 1, 2]);

            chart = new google.visualization.ComboChart(document.getElementById('report_graph'));
            chart.draw(view, options);
        } else {
            console.log('No data to display');
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
            _drawChart(resp);
        });
    };

    // display the chart on page init
    google.load("visualization", "1", {packages:["corechart"], "callback" : initDrawChart});

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
                        html = '';

                    if (resp.length) {
                        for (i; i < resp.length; i+=1) {
                            html += [
                                '<tr id="js_session_' + resp[i].id + '" class="log_row js_log_' + this_id + '">',
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
            _drawChart(resp);
        });
    });
}); // end document ready