/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log, Highcharts*/
'use strict';

$(document).ready(function () {
    var this_message_id = $('#js_selectMessage').val(),

        // function
        drawBarChart,
        fetchDataAndDrawChart,
        tabClickHandler;

    // navigate with the dropdown
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });

    // handler after click the tab navs
    tabClickHandler = function (file_index) {
        // send ajax to fetch detail for log table
        $.ajax({
            url: _.template(
                '/report/detail/<%= data.message_id %>/<%= data.file_index %>/',
                {message_id: this_message_id, file_index: file_index}
            ),
            type: 'POST',
            data: {'message_id': this_message_id, 'file_index': file_index},
        }).done(function (resp) {
            // render the table
            $('#tab_' + file_index).html(resp);

            // draw the graph
            fetchDataAndDrawChart(file_index);
        });
    };

    // bind handler to tab navs
    $('.nav-tabs a').click(function () {
        var file_index = $(this).data('index');
        tabClickHandler(file_index);
    });

    // when init page, click on tab 1 to load the 1st file report
    if ($('.nav-tabs li').length) {
        tabClickHandler(1);
    }

    // draw chart function
    drawBarChart = function (json_data) {
        var options,
            len = json_data.values.length,
            bar_width = Math.log(39 / len) * 80; // HIEU's algorithm to set column width nicely

        if (typeof json_data === 'object' && len > 0) {
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
                colors: ['#008CBA'], // match color of top navigation
                tooltip: {
                    useHTML: true,
                    formatter: function () {
                        return _.template('<div class="report_thumbnail"><p><%= data.page %>: <%= data.time %></p><img src="<%= data.img %>" width="250" /></div>', {
                            page: this.x[1],
                            time: CC_GLOBAL.second2time(this.y),
                            img: json_data.imgs[this.x[0]]
                        });
                    }
                },
                series: [{
                    showInLegend: false,
                    data: json_data.values,
                    pointWidth: bar_width,
                }]
            };

            // set the y axis limit to 600 (10 minutes) if there is a page data over that limit
            if (json_data.is_bigger_than_limit) {
                options.yAxis.max = 600;
                options.yAxis.labels = {
                    formatter: function () {
                        if (this.value < 600) {
                            return this.value;
                        }
                        return '600+';
                    }
                };
            }

            // draw chart
            $('.report_graph:visible').highcharts(options);
        } else {
            log('No data to display');
        }
    };

    // fetch data from backend and draw column chart
    fetchDataAndDrawChart = function (file_index) {
        $.ajax({
            url: '/report/drilldown/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': this_message_id,
                'file_index': file_index
            },
        }).done(function (resp) {
            drawBarChart(resp);
        });
    };

    // close the deal when click checkbox
    $('.report_wrapper').on('click', '.js_sold', function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            action = _this.prop('checked') ? 'create' : 'remove',
            id_arr = this_id.replace('row_', '').split('_'),
            message_id = id_arr[0],
            user_id = id_arr[1];

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
    $('.report_wrapper').on('click', '.cell_email', function () {
        var _this = $(this),
            this_row = _this.closest('tr'),
            this_id = this_row.prop('id'),
            id_arr = this_id.replace('row_', '').split('_'),
            message_id = id_arr[0],
            user_id = id_arr[1],
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
                        'file_index': $('.nav-tabs li.active a').data('index')
                    }
                }).done(function (resp) {
                    var i,
                        html = '',
                        html_row = _.template(
                            '<tr id="js_session_<%= data.session_id %>" class="log_row js_log_<%= data.this_id %>"> \
                                <td></td> \
                                <td><%= data.created_ts %></td> \
                                <td></td> \
                                <td><%= data.total_time %></td> \
                                <td></td> \
                                <td><%= data.client_ip %></td> \
                                <td><%= data.device %></td> \
                            </tr>'
                        );

                    if (resp.length) {
                        for (i = 0; i < resp.length; i += 1) {
                            html += html_row({
                                session_id: resp[i].id,
                                this_id: this_id,
                                created_ts: resp[i].created_ts,
                                total_time: resp[i].total_time,
                                client_ip: resp[i].client_ip,
                                device: resp[i].device,
                            });
                        }
                    }
                    this_row.after(html);
                });
            }
        }
    });

    // draw the chart again for each session after click on each session log row
    $('.report_wrapper').on('click', '.log_row', function () {
        var this_session_id = $(this).prop('id').replace('js_session_', '');
        $.ajax({
            url: '/report/drilldown/',
            type: 'POST',
            dataType: 'json',
            data: {
                'message_id': this_message_id,
                'session_id': this_session_id,
                'file_index': $('.nav-tabs li.active a').data('index')
            },
        }).done(function (resp) {
            drawBarChart(resp);
        });

        return false;
    });

    // if there is ?user in GET query then click on it and scroll down a bit
    if (!_.isUndefined(CC_GLOBAL.GETParam.tab)) {
        $('a[href="#tab_' + CC_GLOBAL.GETParam.tab + '"').trigger('click');

        if (!_.isUndefined(CC_GLOBAL.GETParam.user)) {
            $('#user_' + CC_GLOBAL.GETParam.user).trigger('click');
            $(window).delay(500).scrollTop(600);
        }
    }
}); // end document ready