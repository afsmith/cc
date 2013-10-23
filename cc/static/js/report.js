$(document).ready(function () {
    var drawChart;

    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // draw google charts
    drawChart = function () {
        var chart_data,
            data,
            options,
            chart;

        chart_data = $.ajax({
            url: window.location,
            type: 'GET',
            dataType: 'json',
        }).done(function (resp) {
            data = google.visualization.arrayToDataTable($.merge(
                [['Page', 'Total time']],
                resp
            ));

            options = {
                title: 'Page graph',
                hAxis: {
                    //title: 'Page',
                    //titleTextStyle: {color: 'red'},
                    format: 'Page #',
                    gridlines: {
                        count: resp.length
                    }
                },
                height: 500,
            };

            chart = new google.visualization.ColumnChart(document.getElementById('report_graph'));
            chart.draw(data, options);
        });

        
    };
    google.load("visualization", "1", {packages:["corechart"], "callback" : drawChart});
    
    // get page total time and display
    

}); // end document ready