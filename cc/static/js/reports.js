var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.reports.loadReports(this.location.hash.replace(/#/, ''));
    app.listeners.reportsChangeListener();
    $("#id_owner").sb();
    $('#reportDetails').hide();
    $('#importedReportDetails').hide();
    $('#addNewReport').click(function(){
        $.nmManual(
          '/reports/create/',
          {
              callbacks: {
                  beforeShowCont: function(){
                      $('#id_schedule_type').change();
                      $('#id_send_to').change();
                      initDisplayedForm();
                  }
              }
          }
        );
        return false;
    });
    $('#add_receiver').live('click', function(e){
        app.config.searchForm = false;
        e.preventDefault();
/*        var addTag = function(elem){
            var cnf = app.config;
            var els = app.elements;
            var tag = $.trim($(elem + ' option:selected').text());
            console.log(Ing.elements);
            
            var el = new els.tag(tag);
            els.attach(el, cnf.tagList);
        };*/
        var send_to = $('#id_send_to');
        var users = $('#id_send_users');
        var admins = $('#id_send_admins');
        var groups = $('#id_send_groups');
        var receivers = $('#receiversList');
        var selected = '';
        switch(send_to.val()){
            case '0':
                return false
                break;
            case '1':
                selected = $('option:selected', users).text();
                //addTag('#id_send_users');
                app.callbacks.handleTags('#id_send_users', '#tagListUsers');
                break;
            case '2':
                selected = $('option:selected', admins).text();
                app.callbacks.handleTags('#id_send_admins', '#tagListAdmins');
                break;
            case '3':
                selected = $('option:selected', groups).text();
                app.callbacks.handleTags('#id_send_groups', '#tagListGroups');
                break;
        }
        return false;

    });
    $('#importNewReport').live('click', function(){
        $.nmManual(
          '/administration/reports/create/',
          {
              callbacks: {
                  beforeShowCont: function(){
                      $('#id_schedule_type').change();
                      $('#id_send_to').change();
                      initDisplayedForm();
                  }
              }
          }
        );
        return false;
    });

    $('#id_owner').change(function() {
        $('.reportName').each(function() {
            if ($('#id_owner').val() && $('#id_owner').val() != $(this).attr('ownerid')) {
                $(this).parent('li').hide();
            } else {
                $(this).parents('li').show();
            }
        });
    });

    app.helpers.trimming($('#id_note'), 400, true);

    $('#removeReport').live('click', function(){
        if(app.data.activeReport){
            app.helpers.window(
               t.SYSTEM_MESSAGE,
               t.REPORT_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
               [{
                   'text': t.YES,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.nmTop().close();
                           $.get(
                               "/reports/delete/" + app.data.activeReport.id + "/",
                               function(data){
                                if(data.status == "OK") {
                                    $('#reportDetails').hide();
                                    $('#importedReportDetails').hide();
                                    app.reports.loadReports();
                                }
                            });
                           return false;
                       }
                   }]
               },{
                   'text': t.NO,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.nmTop().close();
                           return false;
                       }
                   }]
               }],
               false
           );
       }
       return false;
    });

    $('#removeImportedReport').live('click', function(){
        if(app.data.activeReport){
            app.helpers.window(
               t.SYSTEM_MESSAGE,
               t.REPORT_TEMPLATE_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
               [{
                   'text': t.YES,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.nmTop().close();
                           $.get(
                               "/administration/reports/delete/" + app.data.activeReport.id + "/",
                               function(data){
                                if(data.status == "OK") {
                                    $('#reportDetails').hide();
                                    $('#importedReportDetails').hide();
                                    app.reports.loadReports();
                                }
                            });
                           return false;
                       }
                   }]
               },{
                   'text': t.NO,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.nmTop().close();
                           return false;
                       }
                   }]
               }],
               false
           );
       }
       return false;
    });

    $('#editReport').click(function(){
       if(app.data.activeReport){
           $.nmManual(
              '/reports/create/' + app.data.activeReport.id + '/',
              {
                  callbacks: {
                      beforeShowCont: function(){
                          $('#id_schedule_type').change();
                          $('#id_send_to').change();
                          initDisplayedForm();
                          $('#chooseTemplate').before('<span class="fileName">' + app.data.activeReport.template_path + '</span>');
                          $('#chooseTemplate').text(t.CHANGE);
                      }
                  }
              }
           );
        }
        return false;
    });

    $(document).on('click','#editImportedReport', function(){
       if(app.data.activeReport){
           $.nmManual(
              '/administration/reports/create/' + app.data.activeReport.id + '/',
              {
                  callbacks: {
                      beforeShowCont: function(){
                          $('#id_schedule_type').change();
                          initDisplayedForm();
                          $('#chooseTemplate').before('<span class="fileName">' + app.data.activeReport.template_path + '</span>');
                          $('#chooseTemplate').text(t.CHANGE);
                      }
                  }
              }
           );
        }
        return false;
    });

    $('#runReport').click(function(){
       if(app.data.activeReport && !$(this).hasClass('button-disabled')){
           $(this).addClass('button-disabled');
           $(this).text(t.REPORT_QUEUED);
           $.post(
              '/reports/generate/' + app.data.activeReport.id + '/',
              function(data){
                  /*if(data.status == 'OK'){
                      $('#runReport').removeClass('button-disabled');
                  }*/
              }
           );
        }
        return false;
    });
    $('#id_send_to').live('change', function(){
        var send_users = $('#id_send_users');
        var send_users_par = send_users.parents('li');
        var send_admins = $('#id_send_admins');
        var send_admins_par = send_admins.parents('li');
        var send_groups = $('#id_send_groups');
        var send_groups_par = send_groups.parents('li');

        send_users.attr('disabled', 'disabled');
        send_users_par.hide();
        send_admins.attr('disabled', 'disabled');
        send_admins_par.hide();
        send_groups.attr('disabled', 'disabled');
        send_groups_par.hide();
        switch($(this).val()){
            case '0':
                send_users.attr('disabled', 'disabled');
                send_users_par.hide();
                send_admins.attr('disabled', 'disabled');
                send_admins_par.hide();
                send_groups.attr('disabled', 'disabled');
                send_groups_par.hide();
                break;
            case '1':
                send_users_par.show();
                send_users.removeAttr('disabled')
                    .sb('refresh');
                break;
            case '2':
                send_admins_par.show();
                send_admins.removeAttr('disabled')
                    .sb('refresh');
                break;
            case '3':
                send_groups_par.show();
                send_groups.removeAttr('disabled')
                    .sb('refresh');
                break;
                
        }
    });
    $('#id_schedule_type').live('change', function(){
        $('#id_schedule_day_month').parents('li').hide();
        $('#id_schedule_day_month').attr('disabled', 'disabled');
        $('#id_schedule_day_week').parents('li').hide();
        $('#id_schedule_day_week').attr('disabled', 'disabled');
        $('#id_schedule_hour').parents('li').hide();
        $('#id_schedule_hour').attr('disabled');
        switch($(this).val()){
            case '1':
                $('#id_schedule_day_week').parents('li').show();
                $('#id_schedule_day_week').removeAttr('disabled');
                $('#id_schedule_hour').parents('li').show();
                // $('#id_schedule_hour').removeAttr('disabled');

                break;
            case '2':
                $('#id_schedule_day_month').parents('li').show();
                $('#id_schedule_day_month').removeAttr('disabled');
                $('#id_schedule_hour').parents('li').show();
                // $('#id_schedule_hour').removeAttr('disabled');
                break;
            case '3':
                $('#id_schedule_hour').parents('li').show();
            default:
                break;
        }
        $('#newReportForm select[id*="id_schedule"]').not("#id_schedule_type").sb('refresh');
        $('ul.selectbox').css("width","auto");
    });
    $('#newReportForm a.button-submit').live('click', function(){
                var form = $(this).parents('form');
				form.find('input:disabled.hasDatepicker').removeAttr('disabled');
                var formExtend = form.children('.formExtend');
                var rcvListUsers = formExtend.find('ul#tagListUsers');
                var rcvListAdmins = formExtend.find('ul#tagListAdmins');
                var rcvListGroups = formExtend.find('ul#tagListGroups');
                var send_report = $('#id_send_report').attr('checked');
                var usersList = [];
                var adminsList = [];
                var groupsList = [];
                rcvListUsers.children('li').each(function(){
                    usersList.push($.trim($(this).text()));
                });
                rcvListAdmins.children('li').each(function(){
                    adminsList.push($.trim($(this).text()));

                });
                rcvListGroups.children('li').each(function(){
                    groupsList.push($.trim($(this).text()));

                });
                $('<input type="text" id="norifyUsers" name="notifyUsers" style="display: none" value="'+usersList.join(',')+'" />').appendTo(form);
                $('<input type="text" id="norifyAdmins" name="notifyAdmins" style="display: none" value="'+adminsList.join(',')+'" />').appendTo(form);
                $('<input type="text" id="norifyGroups" name="notifyGroups" style="display: none" value="'+groupsList.join(',')+'" />').appendTo(form);

                if ((!usersList.length && !adminsList.length && !groupsList.length) &&
                    send_report) {
                    $('#id_send_report').parents('li').append('<div class="formError">You haven\'t specified any receivers.</div>')
                    return false;
                }
				form.submit();
				return false;
    });
    $('#newReportForm').live('submit', function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
           success: function(data){
               try{
                   data = $.parseJSON(data);
                   if(data.status == "OK"){
                    $('.nyroModalClose').trigger('click');
                    app.reports.loadReports();
                    $('#reportDetails').hide();
                    $('#importedReportDetails').hide();
                    return false;
                   }else{

                   }
               }catch(e){
                   $('.nyroModalLink').html(data);
                   initDisplayedForm();
                   $('#id_send_users').closest('li').hide();
                   $('#id_send_admins').closest('li').hide();
                   $('#id_send_groups').closest('li').hide();
                   $('.nyroModalLink a.close').click(function(){
                	   $.nmTop().close();
                   });
               }
           }
        });
        return false;
    });
    $('#reportFilter').keyup(function(){
        $('.reportName').each(function(){
            if($(this).html().toLowerCase().indexOf($.trim($('#reportFilter').val().toLowerCase())) == -1){
                $(this).parents('li').hide();
            }else{
                $(this).parents('li').show();
            }
        });
    }).focus(function(){
        $(this).select();
    });

	 $('#id_user_required').live('change', function(){
	 	 if ($(this).is(':checked'))
       	$('#id_user_shown').attr('checked', 'checked');
    });

    $('#id_group_required').live('change', function(){
	 	 if ($(this).is(':checked'))
       	$('#id_group_shown').attr('checked', 'checked');
    });

    $('#id_course_required').live('change', function(){
	 	 if ($(this).is(':checked'))
       	$('#id_course_shown').attr('checked', 'checked');
    });

    $('#id_user_shown').live('change', function(){
	 	 if (!$(this).is(':checked'))
       	$('#id_user_required').attr('checked', '');
    });

    $('#id_group_shown').live('change', function(){
	 	 if (!$(this).is(':checked'))
       	$('#id_group_required').attr('checked', '');
    });

    $('#id_course_shown').live('change', function(){
	 	 if (!$(this).is(':checked'))
       	$('#id_course_required').attr('checked', '');
    });

    $('#id_admin_shown').live('change', function(){
	 	 if (!$(this).is(':checked'))
       	$('#id_admin_required').attr('checked', '');
    });

    $('#id_admin_required').live('change', function(){
	 	if ($(this).is(':checked'))
       		$('#id_admin_shown').attr('checked', 'checked');
    });

    var flip = function(from, to) {
        var tmp = $(from).html();
        $(from).html($(to).html());
        $(to).html(tmp);
        $(from).sb('refresh');
        $(from).change();
    };

    $('#show_all').live('change', function() {
        flip('#id_user', '#id_all_users');
        flip('#id_group', '#id_all_groups');
        flip('#id_course', '#id_all_courses');
        flip('#id_admin', '#id_all_admins');
    });

		var searchDefault = $('#reportFilter').val();
		$('#reportFilter').focus(function() {
			if(searchDefault == $('#reportFilter').val()) {
				$('#reportFilter').val('');
			}
		});
		$('#reportFilter').blur(function() {
			if($('#reportFilter').val() == '') {
				$('#reportFilter').val(searchDefault);
			}
		});
});

var initDisplayedForm = function(){
  var template_report_id = $('#id_template_report').val();
  if (template_report_id)
  	set_report_details(template_report_id);

  $('input[type="file"]').each(function(){
    if($(this).attr('id') != 'id_template'){
        $(this).remove();
    }
  });
  $('#newReportForm select').sb();
  $('#id_schedule_type').change();
  $('#id_template').hide();

  $('#id_datepicker_from, #id_datepicker_to').datepicker({
        showOn: "button",
        buttonImage: mediaURL + "img/blank.gif",
        buttonImageOnly: true,
        dateFormat: 'yy-mm-dd'
  });
  $('#id_schedule_hour').timepicker({
        showOn: "button",
        buttonImage: mediaURL + "img/blank.gif",
        buttonImageOnly: true
  });
  $('<a />')
  .attr('id', 'chooseTemplate')
  .addClass('button-normal button-big-no-width')
  .text(t.UPLOAD_JRXML)
  .insertAfter('#id_template');
  $('#chooseTemplate').file().choose(function(e, input) {
      $('.fileName').remove();
      $(this).before('<span class="fileName">' + input.val() + '</span>');
      $(this).text(t.CHANGE);
      input.attr("style", "display: none;");
      input.attr("id", "id_template");
      input.attr("name", "template");
      $("#id_template").replaceWith(input);
  });

  $(".nyroModalClose, .nyroModalBg").live('click', function() {
    $("div.custom-file-input").remove();
  });

  $('#id_template_report').live('change', function(){
  	set_report_details($(this).val());
  });

  $("#id_schedule_hour").attr("readonly","readonly");

  $('#id_name, #id_template_report').parents(".inputWrapper").siblings("label").append('<span class="required">*</span>');
  update_ntf_tags();

  function update_ntf_tags() {
    // -- adding tags to internal data sotrage
    app.config.searchForm = false;
    if(!app.data.tags){
        app.data.tags = [];
    }
    $('#tagListUsers').children('li').each(function(){
       app.data.tags.push({id: $(this).attr('id').replace('tag_', ''), name: $.trim($(this).text())});
    });
    $('#tagListAdmins').children('li').each(function(){
       app.data.tags.push({id: $(this).attr('id').replace('tag_', ''), name: $.trim($(this).text())});
    });
    $('#tagListGroups').children('li').each(function(){
       app.data.tags.push({id: $(this).attr('id').replace('tag_', ''), name: $.trim($(this).text())});
    });
    // -- applying default tag behavior to tags read from server-side
    var helper = new app.elements.tag('dummy tag');
    $('#tagListUsers').children('li').click(function(){
        helper.events[0].handler.apply(this, arguments);
    });
    var helper = new app.elements.tag('dummy tag');
    $('#tagListAdmins').children('li').click(function(){
        helper.events[0].handler.apply(this, arguments);
    });
    var helper = new app.elements.tag('dummy tag');
    $('#tagListGroups').children('li').click(function(){
        helper.events[0].handler.apply(this, arguments);
    });
  }

  function set_report_details(id) {
    //console.log('id = '+id);
    var url = '/reports/get_details/';
    if(id!='') {
        url += id + '/?format=json';
    }
  	$.get(
        url,
        function(data){
            if(typeof data != 'object'){ // IE bug --
                data = $.parseJSON(data);
            }
            if (data.user_shown)
            	$('#id_user').parents('li').show();
            else
            	$('#id_user').parents('li').hide();
            if (data.user_required)
                if ( !$('#id_user').parents(".inputWrapper").siblings("label").find(".required").length ) { $('#id_user').parents(".inputWrapper").siblings("label").append('<span class="required">*</span>'); }

            if (data.group_shown)
            	$('#id_group').parents('li').show();
            else
            	$('#id_group').parents('li').hide();
            if (data.group_required)
                if ( !$('#id_group').parents(".inputWrapper").siblings("label").find(".required").length ) { $('#id_group').parents(".inputWrapper").siblings("label").append('<span class="required">*</span>'); }

            if (data.course_shown)
            	$('#id_course').parents('li').show();
            else
            	$('#id_course').parents('li').hide();
            if (data.course_required)
                if ( !$('#id_course').parents(".inputWrapper").siblings("label").find(".required").length ) { $('#id_course').parents(".inputWrapper").siblings("label").append('<span class="required">*</span>'); }

            if (data.admin_shown)
            	$('#id_admin').parents('li').show();
            else
            	$('#id_admin').parents('li').hide();
            if (data.admin_required) {
                if ( !$('#id_admin').parents(".inputWrapper").siblings("label").children(".required").length ) { $('#id_admin').parents(".inputWrapper").siblings("label").append('<span class="required">*</span>'); }
            }

            if (data.date_from_shown)
            	$('#id_datepicker_from').parents('li').show();
            else
            	$('#id_datepicker_from').parents('li').hide();

            if (data.date_to_shown)
            	$('#id_datepicker_to').parents('li').show();
            else
            	$('#id_datepicker_to').parents('li').hide();
    });
  }
}
