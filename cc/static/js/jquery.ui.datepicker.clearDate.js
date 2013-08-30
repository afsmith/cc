/**
 * Extending jQuery UI Datepicker widget.
 *
 * @author Bartek Liebek
 */
var _generateHTML = $.datepicker._generateHTML;

$.datepicker._generateHTML = function(arguments){
    var html = _generateHTML.call(this, arguments);

    htmlNew = html+'<span class="ui-datepicker-clearField-container">' +
            '<a href="#" class="ui-state-default ui-datepicker-clearField">' + t.CLEAR_DATE + '</a></span>';
    $('.ui-datepicker-clearField').live('click', function(){
				if ( $($.datepicker._lastInput ).parents('form').attr("id") == "newReportForm" ) {
						$($.datepicker._lastInput).val('').trigger('change');
				}
				else {
						$($.datepicker._lastInput).val(t.DATE_NOT_SET).trigger('change');
				}
        $.datepicker._hideDatepicker();
        return false;
    });

		if ( $($.datepicker._lastInput ).attr("id") != "id_schedule_hour" ) {
				return htmlNew;
		}
		else {
				return html;

		}

}
