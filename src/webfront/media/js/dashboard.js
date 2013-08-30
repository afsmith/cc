var app = new Ing();
var ldap_error = false;

$(document).ready(function() {
    app.config.mediaURL = mediaURL;
    app.run();
    app.fitAdminTools = function() {
    	var menuHeight, contHeight, menuHeightDiff;
    	
    	app.helpers.throbber('#adm_toolsTab', 'remove');
    	$('#adm_categories').attr('style', '');
    	menuHeight = $('#adm_categories').outerHeight();
    	menuHeightDiff = menuHeight - $('#adm_categories').height();
		contHeight = $('.modalContent').innerHeight();
    	
    	if (menuHeight < contHeight){
    		$('#adm_categories').height(contHeight - menuHeightDiff);
    	} else {
    		$('.modalContent').attr('style', function(i, currentStyle) { 
    			return currentStyle + '; height: ' + menuHeight + 'px !important;';
    		});
    	}
    }
    
    var fitAdminTools = app.fitAdminTools;

    var savedMsg = '<div class="admSettingsSaved modalContent"><span>' + t.SETTING_SAVED + '</span></div>';
    
    // -- initializing widgets
    $('.widget').each(function() {
        var w = new window["app"]["widgets"][$(this).attr('id')]($(this).attr('id'));
        w.init();
    });

    $('.nyroModal').nyroModal({
        callbacks: {
            'beforeShowCont': function(){
                // -- LDAP widget specific
                $('#id_group_type').sb();
                $('#id_use_ldap').change();

                // -- GUI
                $('#id_default_language').sb();
                $('#id_use_dms').change();
                // -- CONTENT

                $('#id_quality_of_content').sb();

                // -- Fix for SAFARI browser
                $('ul.selectbox').css("width","auto");
            }
        }
    });
    $('.createLDAP').live('click', function(){
       app.helpers.throbber('#ldapGroupList');
       var items = $(this).parent('span').siblings('span').children('input');
       var cn = $('#ldapGroupList li:last').hasClass('odd') ? 'even' : 'odd';
       var data = {
           'action': 'add',
           'data' : { id : "1", group_name : "1", group_dn : "do=1"}
           // 'data': {}
       };
       $(items).each(function() {
           if($(this).attr('type') == 'checkbox'){
               data.data[$(this).attr('name')] = $(this).attr('checked') ? true : false;
           }else{
               data.data[$(this).attr('name')] = $(this).val();
           }
       });


     $('#ldapGroupList').append('<li class="' + cn + '">' +
        '<input type="hidden" name="group_id" value="' + data.id + '" />' +
        '<span title="' + $(items[0]).val() + '"><input type="text" name="group_name" id="id_group_name_edit" maxlength="255" value="' + $(items[0]).text() + '" /></span>' +
        '<span title="' + $(items[1]).val() + '"><input type="text" name="group_dn" id="id_group_dn_edit" maxlength="255" value="' + $(items[1]).text() + '" /></span>' +
        '<span class="narrow"><a class="addLDAP button-normal" href="#">' + t.ADD + '</a>' +
        '&nbsp;<a class="removeLDAPinstant button-normal" href="#">' + t.REMOVE + '</a></span></li>');

        $('#ldapGroupList').animate({
            scrollTop: $('#ldapGroupList').attr("scrollHeight") - $('#ldapGroupList').height()
            },
            300
        );

        $(items).each(function(){
            $(this).attr('checked') ? $(this).removeAttr('checked') : $(this).val('');
        });

        app.helpers.throbber('#ldapGroupList', 'remove');

        return false;
    });


    $('.addLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var items = $(this).parent('span').siblings('span').children('input');
        var data = {
           'action': 'add',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $(items).each(function(){
            data.data[$(this).attr('name')] = $(this).val();
 	    });

		$.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
           		app.helpers.throbber('#ldapGroupList', 'remove');
	            if (data.status == "OK") {
	           		$('#LDAPstatus').html('<span class="success">' + data.message + '</span>');
	            	$(items).each(function(){
			        	$(this).parent().attr('title',$(this).val());
			            $(this).replaceWith($(this).val());
			 	    });
			        $('#ldapGroupList li:last .addLDAP').replaceWith('<a class="editLDAP button-normal" href="#">' + t.EDIT + '</a>');
			        $('#ldapGroupList li:last .removeLDAPinstant').addClass('removeLDAP').removeClass('removeLDAPinstant');
			        $('#ldapGroupList li:last span:last').append('<a class="synchronizeLDAP button-normal" href="#">' + t.SYNCHRONIZE + '</a>');
			        $('#ldapGroupList li:last input[type=hidden]').val(data.id);
            	}
            	else {
            		$('#LDAPstatus').html('<span class="error">' + data.message + '</span>');
		  	    	ldap_error = true;
            	}
        });

        return false;
    });

    $('.editLDAP').live('click', function(){
       var items = $(this).parent('span').siblings('span');
       $(items[0]).html('<input type="text" name="group_name" ' +
        'id="id_group_name_edit" maxlength="255" value="' + $(items[0]).text() + '" />');
       $(items[1]).html('<input type="text" name="group_dn" ' +
        'id="id_group_dn_edit" maxlength="255" value="' + $(items[1]).text() + '" />');

       $(this).replaceWith('<a class="saveLDAP button-normal" href="#">' + t.SAVE + '</a>');
    });
    $('.saveLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var items = $(this).parent('span').siblings('span').children('input');
        var data = {
           'action': 'edit',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $(items).each(function(){
            data.data[$(this).attr('name')] = $(this).val();
        });
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
           		app.helpers.throbber('#ldapGroupList', 'remove');
           		if (data.status == "OK") {
	           		$('#LDAPstatus').html('<span class="success">' + data.message + '</span>');
	           		$(items).each(function(){
			        	$(this).parent().attr('title',$(this).val());
			            $(this).replaceWith($(this).val());
	          		});

		        	$(this).replaceWith('<a class="editLDAP button-normal" href="#">' + t.EDIT + '</a>');
	           	}
           		else {
	        		$('#LDAPstatus').html('<span class="error">' + data.message + '</span>');
        		}
           }
        );

        return false;
    });
    $('.removeLDAPinstant').live('click', function() {
        $(this).parents('li').remove();
        $('#ldapGroupList li').removeClass('odd even').addClass(function(){
            return $(this).index() % 2 ? 'even' : 'odd';
        });
        return false;
    });
    $('.removeLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var data = {
           'action': 'delete',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#ldapGroupList', 'remove');
           }
        );
        $(this).parents('li').remove();
        $('#ldapGroupList li').removeClass('odd even').addClass(function(){
            return $(this).index() % 2 ? 'even' : 'odd';
        });
        return false;
    });
    $('.synchronizeLDAP').live('click', function(){
        app.helpers.throbber('#ldapGroupList');
        var data = {
           'action': 'synchronize',
           'data': {}
        };
        var elem = $(this).parent('span').siblings('input');
        data.data.id = elem.val();
        $.post(
           '/administration/ldap-groups/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#ldapGroupList', 'remove');
           }
        );
        return false;
    });
    $('#id_use_ldap').live('change', function(){
        var elements = $('#LDAPSettingsForm :input').not(this);
        if($(this).attr('checked')){
            elements.removeAttr('disabled');
            //$('#LDAPSettingsForm a').removeClass('button-disabled');
        }else{
            elements.attr('disabled', true);
            //$('#LDAPSettingsForm a').addClass('button-disabled');
        }
        $('#id_group_type').sb('refresh');
    });
    $('#LDAPSettingsForm a').live('click', function(){
        if(!($(this).hasClass('button-disabled'))){
						 $.post(
                 $(this).parents('form').attr('action'),
                 $(this).parents('form').serialize(),
                 function(data, status, xmlHttpRequest) {
                     if (xmlHttpRequest.status == 201) {
                        $('#adm_toolsTab #selectedMessage').html(savedMsg);
                        //new app.widgets['administrative_tools']('administrative_tools').init();
                        //$.nmTop().close();
                    } else {
                        $('#adm_toolsTab #selectedMessage').html(data);
                        $('#id_group_type').sb();
                        $('#id_use_ldap').change();
                        //$('.nyroModalLink').html(data);
                    }
                    fitAdminTools();
                 });
        }
        return false;
    });
    $('#ContentSettingsForm a').live('click', function() {
    	 //$(this).parents('form').submit();

			// $.post(
			//			$(this).parents('form').attr('action'),
			//			$(this).parents('form').serialize(),
			//			function(data, status, xmlHttpRequest) {
			//					//new app.widgets['administrative_tools']('administrative_tools').init();
			//					$.nmTop().close();
			//			});

        $.post(
            $(this).parents('form').attr('action'),
            $(this).parents('form').serialize(),
            function(data, status, xmlHttpRequest) {
                if (xmlHttpRequest.status == 201) {
                    $('#adm_toolsTab #selectedMessage').html(savedMsg);
                } else {
                    $('#adm_toolsTab #selectedMessage').html(data);
                    $('#id_quality_of_content').sb();
                    $('.nyroModalLink a.close').click(function(){
                        $.nmTop().close();
                    });
                }
                fitAdminTools();
        });

        return false;
    });
    $('#SelfRegisterSettingsForm a').live('click', function() {
				$.post(
						$(this).parents('form').attr('action'),
						$(this).parents('form').serialize(),
						function(data, status, xmlHttpRequest) {
								if (xmlHttpRequest.status == 201) {
                                    $('#adm_toolsTab #selectedMessage').html(savedMsg);
									// new app.widgets['administrative_tools']('administrative_tools').init();
									// $.nmTop().close();
								} else {
                                    $('#adm_toolsTab #selectedMessage').html(data);
									//$('.nyroModalLink').html(data);
								}
								fitAdminTools();
				});

        return false;
    });


    $('#id_use_dms').live('change', function(){
        if($(this).attr('checked')){
            $("#id_url_for_dms").removeAttr('disabled');
        }else{
            $("#id_url_for_dms").attr('disabled', true);
        }
    });
	$.ajaxSetup({
		error: function(xhr,msg,err){
			//console.log(xhr);
			//console.log(msg);
			//console.log(err);
		}
	})
    $('#GUISettingsForm a#submit').live('click', function(){
        try {
            $(this).parents('form').ajaxSubmit({
                success: function(data) {
                    if(data.status == "OK") {
                        $('#adm_toolsTab #selectedMessage').html(savedMsg);
                    } else {
                        $('#GUISettingsForm div.error').remove()
                        $('#GUISettingsForm').prepend($('<div>').addClass('error').append(data.message));
                    }
                    fitAdminTools();
                    //TODO handle errors
                },
                dataType: 'json'
            });
        }catch(err) {
            alert(err)
        }
        return false;
    });

    $('#id_use_logo_as_title').live('change', function(){
        if($(this).attr('checked')){
//            console.log('checked');
        }else{
            var label = $(this).attr('id');
            label = label.split('id_')[1];
            //$("#id_url_for_dms").attr('disabled', true);
            var data = {
                'action': 'delete',
                'data': label,
                'scope': 'GUI_SETTINGS_ENTRY_MAP'
            };
            $.post(
                '/administration/gui-settings/',
                JSON.stringify(data),
                function(data){
                    app.helpers.throbber('#GUISettingsForm', 'remove');
                }
            );
        }
    });

    $("#GUISettingsForm .file").live('change', function() {
        var span = $(this).prev();
        span.text($(this).attr("value"));
    });

    $("#GUISettingsForm #logo_file").live('change', function() {
        // Check if logo file is uploaded
        //  if is, enable 'use_as_logo' checkbox
        var checkbox = $("#id_use_logo_as_title");
        if(checkbox.attr('disabled')){
            checkbox.removeAttr("disabled");
        }
    });

    $("#logo_file-back_to_default").live('click', function() {
        // Check if logo file is uploaded
        //  if isn't, disable 'use_as_logo' checkbox
        var checkbox = $("#id_use_logo_as_title");
        if(! checkbox.attr('disabled')){
            checkbox.attr("disabled", "disabled");
            checkbox.removeAttr("checked");
            checkbox.trigger("change");
        }
    });

    $("#GUISettingsForm a.back_to_default").live('click', function() {
        var file = $(this).prev().prev();
        file.removeAttr("value");
        var span = file.prev();
        span.text(span.attr("filename"));
    });

    $("#application_icons-back_to_default, #css_file-back_to_default, #filetype_icons-back_to_default, #progress_icons-back_to_default, #main_menu_bar-back_to_default, #logo_file-back_to_default, #bg_file-back_to_default").live('click',function() {
        app.helpers.throbber('#GUISettingsForm');
        var label = $(this).attr('id');
        var action = label.substr(0, label.indexOf('-'));
        var data = {
           'action': 'delete',
           'data': action
        };
        $.post(
           '/administration/gui-settings/',
           JSON.stringify(data),
           function(data){
             app.helpers.throbber('#GUISettingsForm', 'remove');
           }
        );

		// TODO: Move to backend

		var file;
        switch(action)
        {
        	case 'logo_file':
        		file = 'default_logo';
        		break;
        	case 'bg_file':
        		file = 'kneto-bg.png';
        		break;
        	case 'css_file':
        		file = 'default.less';
        		break;
        	case 'application_icons' :
        		file = 'sprite_icons.png';
        		break;
        	case 'filetype_icons' :
        		file = 'sprite_file_type.png';
        		break;
        	case 'progress_icons' :
        		file = 'sprite_progress.png';
        		break;
        	case 'main_menu_bar' :
        		file = 'sprite_wide.png';
        		break;
        }
        $('#' + action + '_span').text(''+ file + '');
        $('#' + action + '_span').attr("href", app.config.mediaURL+'custom/'+file);
        return false;
    });

    $("#ldapGroupWrapper .button-close").live('click', function() {
		  new app.widgets['administrative_tools']('administrative_tools').init();
    	$.nmTop().close();
    	return false;
    });

    $('#adm_categories li').live('click', function(){
    	$('#selectedMessage').empty();
    	app.helpers.throbber('#adm_toolsTab');
    	$("div.custom-file-input").remove();
        $(this).addClass('active');
        $(this).siblings('li').removeClass('active');
    });

    $('#adm_content').live('click', function(){
        $.get('/administration/content-settings/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            $('#id_quality_of_content').sb();
            $('#id_use_dms').change();
            fitAdminTools();
        });
    });
    $('#adm_gui').live('click', function(){
        $.get('/administration/gui-settings/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            $('#id_default_language').sb();
            fitAdminTools();
        });
    });
    $('#adm_reports').live('click', function(){
        $.get('/administration/reports/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            app.reports.loadReports();
            //$('#id_default_language').sb();
            fitAdminTools();
        });
    });
    $('#adm_registration').live('click', function(){
        $.get('/administration/self-register-settings/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            $('#selectMessageTemplate').sb();
            $('#selectMessageTemplate').change();
            fitAdminTools();
        });
    });
    $('#adm_messages').live('click', function(){
        $.get('/messages/templates/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            fitAdminTools();
        });
    });
    $('#adm_ldap').live('click', function(){
        $.get('/administration/ldap/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            $('#id_group_type').sb();
            $('#id_use_ldap').change();
            fitAdminTools();
        });
    });
    $('#adm_ldap_groups').live('click', function(){
        $.get('/administration/ldap-groups/', function(data) {
            $('#adm_toolsTab #selectedMessage').html(data);
            //$('#id_group_type').sb();
            //$('#id_use_ldap').change();
            fitAdminTools();
        });
    });

});
