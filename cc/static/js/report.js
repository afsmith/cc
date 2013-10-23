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

}); // end document ready