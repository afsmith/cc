$(document).ready(function () {
    var _drawChart,
        initDrawChart,
        this_message_id = $('#js_selectMessage').val();

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
            log'No data to display');
        }
    };

    // fetch data from backend and draw column chart
    /*initDrawChart = function () {
        $.ajax({
            url: '/report/summary/',
            type: 'POST',
            dataType: 'json',
            data: {'message_id': this_message_id},
        }).done(function (resp) {
            _drawChart(resp);
        });
    };*/

    // display the chart on page init
    //google.load("visualization", "1", {packages:["corechart"], "callback" : initDrawChart});


    // click on email address cell
    $('.call_row').click(function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            id_pair = this_id.replace('row_', '').split('_'),
            message_id = id_pair[0],
            user_id = id_pair[1],
            all_log_rows = $('.js_log_' + this_id);

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