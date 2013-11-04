$(document).ready(function () {
    var drawChart;

    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // fetch data from backend and draw column chart
    drawChart = function () {
        $.ajax({
            url: window.location,
            type: 'GET',
            dataType: 'json',
        }).done(function (resp) {
            var data,
                options,
                chart;

            if (resp.length > 0) {
                data = new google.visualization.DataTable();
                data.addColumn({type: 'string', label: 'Page'});
                data.addColumn({type: 'number', label: 'Total time'});
                data.addColumn({type: 'string', role: 'annotation'});
                data.addRows(resp);

                options = {
                    title: 'Page graph',
                    hAxis: {
                        gridlines: {
                            count: resp.length
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
        });
    };

    // display the chart on page init
    google.load("visualization", "1", {packages:["corechart"], "callback" : drawChart});

    // close the deal when click checkbox
    $('.js_sold').click(function () {
        var _this = $(this),
            this_id = _this.closest('tr').prop('id'),
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
            console.log(resp);
            if (resp.status === 'OK') {
                _this.closest('tr').css('color', '#999');
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
            user_id = id_pair[1];

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
                for (i; i < resp.length; i++) {
                    html += ['<tr class="user_log">',
                    '<td></td>',
                    '<td>' + resp[i].created_at + '</td>',
                    '<td></td>',
                    '<td>' + resp[i].total_time/100 + '</td>',
                    '<td></td>',
                    '<td>' + resp[i].client_ip + '</td>',
                    '<td>' + resp[i].device + '</td>',
                    '</tr>'].join('');
                }
            }
            this_row.after(html);
        });
    });

}); // end document ready