$(document).ready(function () {
    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // init the google charts
    function drawChart() {
        var data = google.visualization.arrayToDataTable([
            ['Page', 'Total time'],
            ['Page 1', 23],
            ['Page 2', 25],
            ['Page 3', 27],
            ['Page 4', 3]
        ]);

        var options = {
            title: 'Page graph',
            hAxis: {title: 'Page', titleTextStyle: {color: 'red'}}
        };

        var chart = new google.visualization.ColumnChart(document.getElementById('report_graph'));
        chart.draw(data, options);
    }
    google.load("visualization", "1", {packages:["corechart"], "callback" : drawChart});
}); // end document ready