$(document).ready(function () {
    var _drawPieChart;

    // draw chart function
    _drawPieChart = function (json_data) {
        var chart_data,
            options,
            colors = Highcharts.getOptions().colors,
            len = json_data.values.length,
            column_colors = [],
            bar_width = Math.log(39 / len) * 80,
            i = 0;

        if (typeof json_data === 'object' && len > 0) {
            // change color for key page
            for (i=0; i<len; i+=1) {
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
        } else {
            $('#call_list_graph').html('<p class="alert alert-block">This recipient didn\'t look at your offer</p>')
        }
    };

    // click on each row
    $('.call_row').click(function () {
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
        });
    });
}); // end document ready