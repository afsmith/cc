function User () {
    var me = this;
    me.id = -1,
    me.group = 0,
    me.username = '',
    me.first_name = '',
    me.last_name ='',
    me.email = '',
    me.phone = '',
    me.role = 30,
    me.ocl = false,
    me.send_email = true,

    me.submit = function(){
        $.ajax({
            type: 'POST',
            url: '/management/users/create/',
            data: JSON.parse(JSON.stringify(me)),
            success: function (data, status, xhr) {
                me.id = data.id;
            },
            async: false
        });
    }
}
function Participants (){
    this._defaultGroupName = 'group_',
    this.groupName = '',
    this.members = [],
    this.new_users = [];
    this.users_to_push = {};
    this.error_msg = '',

    this.getGroupName = function(){
        var now = new Date();
        if (this.groupName) {
            return this.groupName;
        }
        this.groupName = this._defaultGroupName +
                    (now.getFullYear()) + '-' +
                    (now.getMonth()+1) + '-' +
                    (now.getDate());
        return this.groupName;
    },
    this.renderNewUsersList = function(oe_class){
        var render_list = [];
        var ele = '';
        $.each(this.new_users, function (count, user) {
            ele = $('<li>').addClass('new_user').addClass(oe_class)
                .append($('<input>').attr('type', 'checkbox')
                                  .attr('name', 'select_new_user')
                                  .attr('id', 'id_select_new_user_'+count)
                                  .attr('value', count));
            ele.append($('<label>').attr('for', 'id_select_new_user_'+count)
                                 .text(user.first_name + ' ' + user.last_name));
            render_list.push(ele);
            ele = '';
            oe_class = oe_class=='even' ? 'odd' : 'even';
        });
        return render_list;
    }
}
var app = new Ing();
var searchTimer = false;
var tim = [];
var selectedGroup = -1;
var participants = new Participants();

$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.ma.loadGroups();
    app.ma.loadActiveModules(this.location.hash.replace(/#/, ''));
    app.data.assignments = {};
    app.config.shelfWrapperWidth = 566;
    app.data.changed = false;
    app.data.search_changed = false;
    app.player.trackUser = false;
    if($("#id_ocl_expires_on").val()=='') {
        $("#id_ocl_expires_on").val(t.DATE_NOT_SET);
    }

    CKEDITOR.config.image_previewText = " ";
    CKEDITOR.config.contentsCss = "/media/css/contentsCKE.css";
    CKEDITOR.config.jqueryOverrideVal = false;
    
    CKEDITOR.on('instanceReady', function (event) {
		event.editor.document.on('drop', function (event) {
			event.data.preventDefault(true);
		});
	});

    $("#id_ocl_expires_on" ).datepicker({
        showOn: "button",
        buttonImage: mediaURL + "img/blank.gif",
        buttonImageOnly: true,
        dateFormat: 'yy-mm-dd',
        minDate: 0,
        defaultDate: +1
    });

    var addMembers = function(groupId) {
        $.each(participants.users_to_push, function(lp, user) {
            user.group = groupId;
            user.submit();
            participants.members.push(user.id);
        });
        data = {
            'action': 'add',
            'members': participants.members
        }
        $.post(
        '/management/groups/' + groupId + '/members/',
        JSON.stringify(data), function(data) {
            if(typeof data != 'object') { // IE bug --
                data = $.parseJSON(data);
            }
        });
    };
    var saveModule = function() {
        var ing = Ing.findInDOM();
        var url = '/content/';
        var groups_ids = [];
        var data = {}
        $.each(app.data.assignments, function (group_id, modules) {
            $.each(modules, function(module_id, is_assigned){
                data = {
                    'module_id': module_id
                };
                groups_ids = [];
                groups_ids = $.parseJSON(app.data.modules[module_id]
                                            ['meta']
                                            ['groups_ids_can_be_assigned_to']);
                groups_ids.push(group_id);
                data['groups_ids'] = groups_ids;
                $.post(
                url,
                JSON.stringify(data), function(data) {
                    if(typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }
                });
            });
        });
    };
    var createNewGroup = function(name){
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var group_id = '';
        $.ajax({
            type: 'POST',
            url: '/management/groups/create/',
            data: 'csrfmiddlewaretoken='+csrf_token+'&name='+name,
            success: function(data, status, xhr){
                if(xhr.status == 201){
                    data = $.parseJSON(data);
                    group_id = data.id
                }else{
                    app.helpers.window(t.SYSTEM_MESSAGE, t.ASS_ERR_GROUP_EXISTS, [{
                        text: t.BTN_CREATE_NEW,
                        events: [{
                            name: 'click',
                            handler: function(e, group_id) {
                            	var modal = $(this).closest('.modalContent'),
                            	    btn_id = $(this).attr('id');
                            	
                            	if (!$(modal).find('.inputWrapper').length) {
	                            	$(modal).find('.windowMessage').html(t.ASS_PROVIDE_GROUP);
	                            	$(modal).find('.windowMessage').after($('#id_new_group_name').parent().clone());
	                            	$(modal).find('#id_new_group_name').attr('id', 'modal_new_group_name')
	                            	$(modal).find('.inputWrapper').css({'width': '220px', 
								                            		  'position': 'relative', 
								                            		  'top': '6px', 
								                            		  'left': '32px'})
	                            	$.each($(modal).find('.windowButtons a'), function(){
	                            		if ($(this).attr('id') != btn_id) { $(this).remove() }
	                            	})
	                            	return false;
                            	}
                                participants.groupName = $('#modal_new_group_name').val();
                                $.nmTop().close();
                                $('#modal_new_group_name').remove();
                                if (!!participants.groupName) { save_assignment(); }
                                return false;
                            }
                        }]
                    },{
                        text: t.BTN_ADD_TO_CURR,
                        events: [{
                            name: 'click',
                            handler: function(e) {
                        		var asg = {},
                        			new_id = -1,
                        			groups = app.data.groups,
                        			groupName = name;
                                $.nmTop().close();
                                $.each(groups, function(){
                                	if (this.name == name) {
                                		new_id = this.id;
                                		return;
                                	};
                                });
                                if (new_id < 0) {return;}
                                $.each(app.data.loadedAssignments[new_id], function(key){
                                	app.data.assignments['-1'][key] = true;
                                });
                                app.data.assignments[new_id] = app.data.assignments['-1'];
                    	        delete(app.data.assignments['-1']);
                    	
                    	        //modify modules: 'can_be_assigned_to'
                    	        saveModule();
                    	        addMembers(new_id);
                			    assign_modules();
                                return false;
                            }
                        }]
                    }], null);
//                    participants.error_msg = t.ASS_GROUP_ERR;
                }
            },
            async: false
        });
        return group_id;
    }
    var showAllModules = function(){
        $('ul.myModules li').removeClass('hidden');
        $('ul.allModules li').removeClass('hidden');
    }
    var createAssignmentPreviewEl = function(module_id, is_even) {
    	var item = document.createElement('li'),
    		label = document.createElement('span');
    	
    	item.setAttribute('id', ['_', module_id].join(''));
    	item.setAttribute('class', is_even ? 'even': 'odd');
    	label.innerHTML = app.data.modules[module_id].meta.title;
    	item.appendChild(label);
    	return item;
    };

    var check_notification_options = function(){
    	if ($('#id_send_email').is(':checked')) {
    		$('.bottomWideContainer input').each(function() {
    			$(this).closest('.bigItem').show();
				if ($(this).attr('name') != "expires_on") $(this).attr('disabled', false);
			});
    		$('#modulePersonalizeBtn').show()
    		$('#modulePreviewBtn').show()
    	} else {
    		$('.bottomWideContainer input').each(function() {
				if ($(this).attr('name') != "send_email") {
					$(this).closest('.bigItem').hide();
					$(this).attr('disabled', true)
				};
			});
    		$('#modulePersonalizeBtn').hide();
    		$('#modulePreviewBtn').hide()
    	}
    };
    
    var checkIfChanged = function() {
    	var currentAssignments = app.data.assignments,
			loadedAssignments = app.data.loadedAssignments,
			currAssignmentsSize = objSize(currentAssignments),
			changed = false;
    	
    	$.each(currentAssignments, function(key, val){
    		if (currAssignmentsSize > 0) {
    			if (objSize(val) != objSize(loadedAssignments[key])) return changed = true;
    			for (assigned in val) {
    				if (!(assigned in loadedAssignments[key])) return changed = true;
    			}
    		} else return;
    	});
    	return changed; 
    }
    
    var clean_checkboxes = function(){
        $('#groupsWrapper input:checked').attr('checked', false);
        $('ul.myModules input:checked').attr('checked', false);
        $('ul.allModules input:checked').attr('checked', false);
    };
    var assignModules = function (modules) {
    	var currentAssignments = app.data.assignments,
    		loadedAssignments = app.data.loadedAssignments;
        modules.each(function(key, val){
        	var moduleId = app.data.map[$(val).attr('id')].id;
            if( $(val).children('span.moduleCheck').children('input').is(':checked')) {
            	currentAssignments[selectedGroup][moduleId] = true;
            } else {
                delete(currentAssignments[selectedGroup][moduleId]);
            }
            if (!parseInt($('#type_group').val())){
	            if (moduleId in loadedAssignments[selectedGroup] != moduleId in currentAssignments[selectedGroup]) {
	            	$(val).closest('li').toggleClass('changed', true);
	            } else {
	            	$(val).closest('li').toggleClass('changed', false);
	            }
            }
        });
    };
    
    var loadPreviewContents = function(group, checkedModules) {
        var messageTemplate = app.helpers.htmlSpecialDecoder($('#messageTemplate').html());
        	iframe = $('#assignmentPreview iframe').contents().find('html');
        	
        $('#messageTemplate').remove();
        $('#modulesPreviewList li').unbind();
        $('#modulesPreviewList ul').empty();
        iframe.html(messageTemplate, group, checkedModules);
        $.each(checkedModules, function(index){
        	$('#modulesPreviewList ul').append(createAssignmentPreviewEl(checkedModules[index], index%2));
        });
      	$('#modulesPreviewList li').on('click', function(event){
      		var playerSize = {'width': 390, 'height': 230},
      			moduleObj = app.data.modules[$(this).attr('id').substring(1)].meta;
      		event.preventDefault();
      		$('#video').empty();
      		$('#assignmentPreviewLesson > span').hide();
      		$('#modulesPreviewList li.selected').toggleClass('selected', false);
      		$(this).toggleClass('selected', true);
            playerParams = {
            	    'contentURL'      : encodeURIComponent('/content/modules/' + moduleObj.id + '/?format=json'),
            	    'cType'           : 'playlist',
            	    'time'            : 10,
            	    'playingIndex'    : 0,
            	    'duration'        : 0,
            	    'siteLanguage'	  : siteLanguage
                }
            
            if (app.config.player.mode == "html5") {
            	app.player.spawnHTML5(playerSize, playerParams, "transparent");
            } else {
            	playerParams.relativeURL = mediaURL;
            	playerParams.contentURL = encodeURIComponent('/content/modules/' + moduleObj.id + '/?format=xml');
            	app.player.spawnFlash("video", playerSize, playerParams, "transparent");  
            	app.player.domInstance = document.getElementById('video');
            }
            return false;
    	});
    };
    
    var applyWysiwyg = function() {
        $("#mailTemplateEdit textarea").each(function (i) {
            var editor = CKEDITOR.replace(this, {"height": "66%", 
            									"resize_enabled": false,
            									"filebrowserUploadUrl": "/messages/upload-image/"});							
            $(this).data("editor", editor);
        });
    };
    
    var getTemplateType = function() {
    	var assigned_modules = 0,
            hash = document.location.hash,
            group_id = $('select#type_group').val();

    	if (parseInt($('select#type_group').val())) {
    		assigned_modules = $('.' + hash.replace(/#/, '')).find('input:checked').length;
    	} else {
    		assigned_modules = $('.' + hash.replace(/#/, '')).find('li.changed input:checked').length;
    	}
    	
    	if (assigned_modules > 1) {
    		return 'assign_to_all';
    	} else {
    		return ($('#id_ocl').is(':checked'))? 'assign_to_one_ocl': 'assign_to_one';
    	}
    };
    
    var parseModulesAssignment = function(event) {
        //Ing.findInDOM().helpers.opaque_throbber(event.delegateTarget);
    	var group_id = parseInt(selectedGroup),
    		currentAssignments = app.data.assignments[group_id],
    		assigned_modules = app.data.loadedAssignments[group_id],
    		target = event.delegateTarget,
    		can_be_assigned = [];
//        clear_search();
        if (group_id < 0 && group_id != -2) {
            //Ing.findInDOM().helpers.throbber(event.delegateTarget, 'remove');
            return
        }
        $.each($(target).find('li'), function(index){
        	var id = $(this).attr('id'),
        		map_obj = app.data.map[id];

            if ('groups_ids_can_be_assigned_to' in map_obj) {
                can_be_assigned = $.parseJSON(map_obj['groups_ids_can_be_assigned_to']);
                if (!!$(this).attr('style') && $(this).css('display') == 'list-item' && can_be_assigned.indexOf(group_id) < 0) {
                	$(this).hide();
                } else {
                    $(this).toggleClass('hidden', !(can_be_assigned.indexOf(group_id) > -1));
                }
            }
            if ('id' in map_obj) {
            	if (!!currentAssignments) {
            		$('#' + id + ' span.moduleCheck input').attr('checked', (map_obj['id'] in currentAssignments));
                    if (assigned_modules.hasOwnProperty(map_obj['id']) != currentAssignments.hasOwnProperty(map_obj['id'])) {
                    	$(this).toggleClass('changed', true);
                    } else {
                    	$(this).toggleClass('changed', false);
                    }
            	} else if (map_obj['id'] in assigned_modules){
            		$('#' + id + ' span.moduleCheck input').attr('checked', true);
            		$(this).toggleClass('changed', false);
            	}
            }
        });
        //Ing.findInDOM().helpers.opaque_throbber(event.delegateTarget, 'remove');
    };
    
    var showConfirmationWindow = function(backToUsers) {
    	group = (parseInt($('select#type_group option:selected').val()) == 0)
			? $('#groupName').html() : $('#id_new_group_name').val()
    	app.helpers.window(t.SYSTEM_MESSAGE, t.ASS_NOTIFY_CHANGE.replace('{groupname}', group),  [{
            text: t.YES,
            events: [{
                name: 'click',
                handler: function(e) {
                    $.nmTop().close();
                    $('#as_save').trigger('click');
                    return false;
                }
            }]
        },{
            text: t.NO,
            events: [{
                name: 'click',
                handler: function(e) {
                    $.nmTop().close();
                    app.data.changed = false;
                    if (backToUsers) {
                    	$('select#type_group').val(parseInt($('select#type_group').val()) ? 0: 1);
                		$('#groupSelectionWrapper .display.selectBoxJs .text')
            				.html($('select#type_group option[value="'+$('select#type_group').val()+'"]').html());
                    	$('select#type_group').trigger('change');
                    } else {
                    	$('#changeGroup').click();
                    }
                    $('#as_cancel').hide();
                    return false;
                }
            }]
        },{
            text: t.CANCEL,
            events: [{
                name: 'click',
                handler: function(e) {
                    $.nmTop().close();
                    return false;
                }
            }]
        }], null);	    	
    };
    
    check_notification_options();
    $('ul.usersList li.new_user input').live('change', function(){
        if ($(this).is(':checked')){
            participants.users_to_push[$(this).val()] =
                participants.new_users[$(this).val()];
        } else {
            delete(participants.users_to_push[$(this).val()]);
        }
    });
    $('#addNewUser').on('click', function(e){
        e.preventDefault();
        $.nmManual(
        '/management/users/create/?type=pending',
        {
            resizable: true,
            callbacks: {
            	beforeShowCont: function() {
            		$('#id_role').sb();
            		$('#newUserForm .sb').closest('li').find('label').css("padding-right", '18px');
            	}
            }
        }
        );
        $('#id_role').sb();
    });
    $('#id_role').live('change', function(){
        if ($(this).val() == 40){
            $('#newUserForm input#id_send_email').removeAttr('checked');
        } else {
            $('#newUserForm input#id_send_email').attr('checked', 'checked');
        }
    });
    $('#sb_pending').live('click', function(e) {
        e.preventDefault();
        var form = $('#newUserForm ul');
        var user = new User();
        user.username = $('#id_username', form).val();
        user.first_name = $('#id_first_name', form).val();
        user.last_name = $('#id_last_name', form).val();
        user.email = $('#id_email', form).val();
        user.phone = $('#id_phone', form).val();
        user.role = $('#id_role', form).val();
        user.ocl = $('#id_ocl', form).val();
        user.send_email = $('#id_send_email', form).val();
        user.group = 0;
        $.post('/management/users/validate_form/',
            JSON.parse(JSON.stringify(user)),
            function(data, status, xhr){
                if (xhr.status==201){
                    participants.new_users.push(user);
                    $.nmTop().close();
                    $('ul.usersList li.new_user').remove();
                    var next_class = $('ul.usersList li').last().hasClass('even') ? 'odd': 'even';
                    $('ul.usersList li').removeClass('last');
                    $.each(participants.renderNewUsersList(next_class), function(count, user) {
                        $('ul.usersList').append(user);
                    });
                    return false;
                } else {
                    $('.modalContent').empty();
                    $('.modalContent').html(data);
                }
            }
        );
    });
    $('#id_send_email').on('change', function(){
        check_notification_options();
    });

    $('#searchGroups').keyup(function(){
        $('#groupsWrapper .result:not(.hidden) li').each(function(){
        	var label = $(this).find('label').length ? $(this).find('label')[0] : $(this).find('span')[0];
        	if (!label) label = this;
            if($(label).html().toLowerCase().indexOf($.trim($('#searchGroups').val().toLowerCase())) == -1){
                $(this).hide();
            }else{
                $(this).show();
            }
        });
    });
    var searchDefault = $('#searchGroups').val();
    var clear_search = function() {
		$('#searchGroups').val('');
		$('#searchGroups').trigger('keyup');
    	$('#searchGroups').val(searchDefault);
    	$('#id_language').val(0);
    	$('#id_language').sb('refresh');
        $('#id_groups').val(0);
        $('#id_groups').sb('refresh');
        $('#search').val('');
        $('#id_groups').trigger('change');
        $('#search').val(searchDefault);
        app.data.search_changed = false;
    }
    var reset_owner = function() {
        $('#id_owner').val($('#id_owner option[selected]').val());
        $('#id_owner').sb('refresh');
        $('#id_owner').trigger('change');
    }
    
    $('#searchGroups').focus(function() {
    	if(searchDefault == $('#searchGroups').val()) {
    		$('#searchGroups').val('');
    	}
    });
    $('#searchGroups').blur(function() {
    	if($('#searchGroups').val() == '') {
    		$('#searchGroups').val(searchDefault);
    	}
    });
    
    $('#changeGroup').live('click', function() {
    	if (app.data.changed) {
    		showConfirmationWindow(0);
    		return;
    	}
		$('#moduleDetailsWrapper').toggleClass('hidden', true);	
        $('.groupsList').removeClass('hidden');
        $('.usersList').addClass('hidden');
        $('#id_new_group_name').parents('.formList').each(function(){
            $(this).addClass('hidden');
        });
        // fix for size of modules tabs
//        $('#modulesWrapper li.first').next().css('left', $('#modulesWrapper li.first').width()-14);
        $('#modulesWrapper').addClass('hidden');
        $('#groupsBar').removeClass('hidden');

        $('ul.groupsList li').removeClass('active');
        $('#groupInformation').addClass('hidden').hide();
        $('.addUser').hide();
        selectedGroup = -1;
        app.data.assignments = {};
        reset_owner();
        clear_search();
        $('#searchGroups').val(searchDefault);
        $('#modulesWrapper').hide();
    });
    
    $('#modulePreviewBtn').click(function(event){
    	event.preventDefault();
    	window.scrollTo(0,0);
    	var checkedIDs = [],
    		savedTemplate = app.data.savedTemplate,
    		checkedModules = {},
    		postData = {},
    		ocl_enabled = ($('#id_ocl').is(':checked') && $('#id_send_email').is(':checked'));
    		group = (parseInt($('select#type_group option:selected').val()) == 0)
    					? $('#groupName').html() : $('#id_new_group_name').val();
    	
    	if (parseInt($('#type_group').val())){
	        $('ul.myModules input:checked').each(function(){
	        	var id = app.data.map[$(this).closest('li').attr('id')]['id'];
	        	if (!!id) checkedIDs.push(id);
	        });
	        $('ul.allModules input:checked').each(function(){
	        	var id = app.data.map[$(this).closest('li').attr('id')]['id'];
	        	if (!!id){
	            	if ($.inArray(id, checkedIDs) < 0) checkedIDs.push(id);
	        	}
	        });
    	} else {
	        $('ul.myModules .changed').find('input:checked').each(function(){
	        	var id = app.data.map[$(this).closest('li').attr('id')]['id'];
	        	if (!!id) checkedIDs.push(id);
	        });
	        $('ul.allModules .changed').find('input:checked').each(function(){
	        	var id = app.data.map[$(this).closest('li').attr('id')]['id'];
	        	if (!!id){
	            	if ($.inArray(id, checkedIDs) < 0) checkedIDs.push(id);
	        	}
	        }); 		
    	}
    	
        $.each(checkedIDs, function(key, value){
        	if (!!app.data.modules[value]) checkedModules[value] = app.data.modules[value].meta.title;
        });
        
        postData = {'group': group, 'modules': checkedModules, 'ocl_enabled': ocl_enabled}
        
        if (!!savedTemplate && savedTemplate.type == getTemplateType())
        	postData['savedTemplate'] = savedTemplate
        	
        $('#mailTemplateEdit').remove();	
        	
    	$.post('/content/modules/preview_assignment/', JSON.stringify(postData), function(data) {
            var bg = $('<div class="modalBg customModalBg"></div>'),
	        	modal = $(data);
	        bg.css({
	        	opacity: 0,
	            height: $(window).height(),
	            width: $(window).width()
	        });
	        modal.attr('id', 'assignmentPreview');
	        modal.css({
	            left: $(window).width() / 2 - 350,
	            top: 10
	        });
	        bg.appendTo($('body'));
	        modal.appendTo($('body'));
	        $('#assignmentPreview .nyroModalCloseButton').click(function(event){
	        	event.preventDefault();
	        	$('#assignmentPreview').animate({
	        	    opacity: 0,
	        	  }, 300, function() {
	        		$('#assignmentPreview').remove();
	        		$('.customModalBg').animate({
	            	    opacity: 0,
	          	  	}, 300, function() {
	          	  		$('#assignmentPreview .nyroModalCloseButton').unbind();
		        		$('.customModalBg').remove();
		        	});
	        	  });
	        });
        	$('.customModalBg').animate({
        	    opacity: 0.7,
      	  	}, 300, function(){
            	$('#assignmentPreview').animate({
            	    opacity: 1,
            	}, 300, function(){
        	        loadPreviewContents(group, checkedIDs);
            	});     	  		
      	  	});
    	}, 'html');
    });
    
    $('#modulePersonalizeBtn').click(function(event){
    	event.preventDefault();
    	window.scrollTo(0,0);
    	var savedTemplate = app.data.savedTemplate,
    		method = (!!savedTemplate)? 'POST': 'GET',
    		ajax = {},
    		postData = {},
    		templateType = getTemplateType(),
			wysiwygInstances = getObjKeys(CKEDITOR.instances);
    	
    	if (!savedTemplate || savedTemplate.type != templateType) {
    		app.data.savedTemplate = null;
    		method = 'GET';
    	}
    	$('#mailTemplateEdit').remove();
    	ajax = {url: '/messages/templates/edit-beforesend/?template=' + templateType, 
        		type: method, success: function(data) {
    	            var bg = $('<div class="modalBg customModalBg"></div>'),
    		        	modal = $(data);
    		        bg.css({
    		        	opacity: 0,
    		            height: $(window).height(),
    		            width: $(window).width()
    		        });
    		        modal.attr('id', 'mailTemplateEdit');
    		        modal.css({
    		        	opacity: 0,
    		            left: $(window).width() / 2 - 350,
    		            top: 10
    		        });
    		        bg.appendTo($('body'));
    		        modal.appendTo($('body'));
    		        applyWysiwyg();
    		        $('.customModalCloseButton, .customModalBg, #messageTemplateForm .button-default, \
    		        		#messageTemplateForm .button-submit').click(function(event){
    		        	event.preventDefault();
    		        	$('#mailTemplateEdit').animate({
    		        	    opacity: 0,
    		        	  }, 300, function() {
    		        		$('#mailTemplateEdit').hide();
    		        		$('#mailTemplateEdit').addClass('hidden');
    		        		for (var i = 0, len = wysiwygInstances.length; i < len; i++) {
	    		        		delete CKEDITOR.instances[wysiwygInstances[i]];
	    		        	}
    		        		$('.customModalBg').animate({
    		            	    opacity: 0,
    		          	  	}, 300, function() {
	    		          	  	$('.customModalCloseButton, .customModalBg, #messageTemplateForm .button-default, \
	    		        		#messageTemplateForm .button-submit').unbind();
    			        		$('.customModalBg').remove();
    			        	});
    		        	  });
    		        });
    	        	$('.customModalBg').animate({
    	        	    opacity: 0.7,
    	      	  	}, 300, function(){
    	            	$('#mailTemplateEdit').animate({
    	            	    opacity: 1,
    	            	}, 300, function(){
    	            	});     	  		
    	      	  	});
        	    }, dataType: 'html'}
    	if (!!savedTemplate) {
    		ajax['data'] = JSON.stringify({'templateData': savedTemplate});
    	}
    	$.ajax(ajax); 
    	return;
    });
    
    $('#mailTemplateEdit .button-submit').live('click', function(ev) {
        ev.preventDefault();
    	var title = $('#messageTemplateSubject input').val(),
    		text = $('#messageTemplate * textarea').data("editor").getData(),
    		defaultCkecked = $('#default_template').is(':checked');

    	if (defaultCkecked) {
    		app.data.savedTemplate = null;
    	} else {
        	app.data.savedTemplate = {'subject': title,
   				  					  'content': text,
   				  					  'type': $('#templateType').val()};    		
    	}

        return false;
    });

    // handling default new group name
    $('#id_new_group_name').keyup(function(){
        participants.groupName = $(this).val();
    });
    $('#id_new_group_name').blur(function(){
        if (! $(this).val()) {
            $(this).val(participants.getGroupName());
        }
    });

    // update members list every time checkbox is change on userlist
    $('ul.usersList li input[type=checkbox]').on('change', function(){
        if ($(this).is(':checked')) {
            participants.members.push($(this).val());
        } else {
            if (participants.members.inArray($(this).val()) ) {
                participants.members.splice(
                    participants.members.indexOf($(this).val()), 1);
            }
        }
    });
    $('span.moduleCheck input[type="checkbox"]').live('change', function(){
        var module = $(this).parent('span').parent('li'),
        	sibling_modules = module.siblings('li');
        if (typeof(app.data.assignments[selectedGroup]) != 'object'){
            app.data.assignments[selectedGroup] = {};
        }
        assignModules(sibling_modules);
        assignModules(module);
        app.data.changed = checkIfChanged();
        $('#as_cancel').toggleClass('forceHidden', !app.data.changed);
    });

    $('select#type_group').live('change', function(){
    	if (app.data.changed) {
    		$('select#type_group').val(parseInt($('select#type_group').val()) ? 0: 1);
    		$('#groupSelectionWrapper .display.selectBoxJs .text')
    			.html($('select#type_group option[value="'+$('select#type_group').val()+'"]').html());
			showConfirmationWindow(1);
    		return;
    	}
		$('#modulesWrapper').show();
		$('#moduleDetailsWrapper').toggleClass('hidden', true);	
        clean_checkboxes();
        $(this).find('option:selected').each(function() {
            if ($(this).val() == 0) {
            	$('.addUser').hide();
                $('.addUser').toggleClass('showOnGroups', true);
                $('.groupsList').removeClass('hidden');
                $('.usersList').addClass('hidden');
                $('#id_new_group_name').parents('.formList').each(function(){
                    $(this).addClass('hidden');
                });
                // fix for size of modules tabs
                $('#modulesWrapper li.first').next().css('left', $('#modulesWrapper li.first').width()-14);
                $('#modulesWrapper').addClass('hidden');
                $('#groupsBar').removeClass('hidden');
                $('#nothingSelectedIndicator').show();
                $('#modulesWrapper').hide();
            } else if ($(this).val() == 1) {
            	$('.addUser').show();
                $('.addUser').toggleClass('showOnGroups', false);
                $('.groupsList').addClass('hidden');
                $('.usersList').removeClass('hidden');
                $('#id_new_group_name').parents('.formList').each(function(){
                    $(this).removeClass('hidden');
                });
                $('#modulesWrapper').removeClass('hidden');
                $('#groupsBar').addClass('hidden');
                reset_owner();
                clear_search();
                showAllModules();
                $('#nothingSelectedIndicator').hide();
                $('#id_new_group_name').val(participants.getGroupName());
                $("a[href='#myModules']").click();
            }
            $('ul#assigned_group_users').empty();
            $('ul#assigned_group_users').addClass('hidden');
        });
        selectedGroup = -1;
        app.data.assignments = {};
        $('#groupInformation').addClass('hidden').hide();

    });

    $('.groupsList li').live('click', function(){
        var group_id = $(this).children('span').attr('id').replace('group_list_', '');
        document.location.hash.replace(/#myModules/, '');
		$('#modulesWrapper').show();
		$('#moduleDetailsWrapper').toggleClass('hidden', true);	
        $(this).siblings('li').removeClass('active');
        $(this).addClass('active');
        $('ul#assigned_group_users').empty();
        $('ul#assigned_group_users').removeClass('hidden');
        $('ul.groupsList').addClass('hidden');

        $.get('/management/groups/'+group_id+'/users/',
            function(data) {
                var className = 'odd';
                $.each(data, function(key, user_dict) {
                    $('ul#assigned_group_users')
                        .append($('<li>')
                            .addClass(className)
                            .text(user_dict['name'])
                        );
                    if (parseInt(user_dict.role) == 40) $('ul#assigned_group_users li').last().addClass('usr_plus');
                    className = className==='odd' ? 'even' : 'odd';
                });
            }
        );
        $('ul.myModules li span.moduleCheck input').attr('checked', false);
        $('ul.allModules li span.moduleCheck input').attr('checked', false);
        $('#groupInformation').removeClass('hidden').show();
        if (group_id == -2) {
            group_name = t.ALL ; 
        } else {
            group_name = app.data.groups[group_id]['name'];
        }
        $('#groupName').text(group_name);
        $('#modulesWrapper').removeClass('hidden');
        selectedGroup = group_id;
        $('#searchGroups').val(searchDefault);
        $("a[href='#myModules']").trigger('click');
    });

    $('select#type_group').trigger('change');
    
    $('#modulesWrapper ul.result').on('loaded', parseModulesAssignment);

    var save_assignment = function() {	
	    if (app.data.assignments.hasOwnProperty(-1)) {
	        //create new group with specified users
	        // and assign it to chosen models
	        new_id = createNewGroup(participants.groupName);
	        if (!new_id) {
	            return false;
	        }
	        app.data.assignments[new_id] = app.data.assignments['-1'];
	        delete(app.data.assignments['-1']);
	
	        //modify modules: 'can_be_assigned_to'
	        saveModule();
	        addMembers(new_id);
	    }
	    assign_modules();
    };
    
    var assign_modules = function() {
    	var asg= {},
    		savedTemplate = app.data.savedTemplate;
	    $.each(app.data.assignments, function(key, value){
	       //if(objSize(value) > 0){
	        asg[key] = [];
	       //}
	       $.each(value, function(subkey, subvalue){
	         asg[key].push(subkey);
	       });
	    });
	    $.post(
	       '/assignments/group/modules/',
	       JSON.stringify({"assignments": asg,
	                       "add_one_click_link": $("#id_ocl").is(':checked') ? 'checked' : '',
	                       "is_sendmail": $("#id_send_email").is(':checked') && $("#id_send_email").is(':checked') ? 'checked' : '',
	                       "allow_login": $("#allow_login").is(':checked'),
	                       "expires_on": $("#id_ocl_expires_on").val(),
	                       "savedTemplate": (!!savedTemplate && savedTemplate.type == getTemplateType())? savedTemplate: null }),
	       function(data){
	         if(typeof data != 'object'){ // IE bug --
	           data = $.parseJSON(data);
	         }
	         if(data.status == 'OK'){
	            app.helpers.window(t.SYSTEM_MESSAGE, t.ASSIGNMENTS_SAVED, null, null, function() {
	                        window.location = "/content/modules/assign/";
	                    });
	         }else{
	           //err
	         }
	         app.helpers.throbber('#group_list', 'remove');
	       }
	    );
    }

	$('#as_save').click(function(e){
        e.preventDefault();
		var users_plus = [];
			usr_list = '';

        show_ocl_warn = true;

        $.each(app.data.assignments, function(k, v){
            if (! getObjKeys(v).length) {
                show_ocl_warn = false;
            }
            if (k>0 && getObjKeys(v) in getObjKeys(app.data.loadedAssignments[k])) {
                show_ocl_warn = false;
            }
        });
		if (parseInt($('#type_group').val())) {
			users_plus = $('.usersList .usr_plus :checked').parent();
		} else {
			users_plus = $('#assigned_group_users').find('li.usr_plus');
		}

		if($('#id_ocl').is(':checked') && !$("#id_send_email").is(':checked')){
			 $("#id_ocl").attr('checked', false);
			 $("#id_ocl").trigger('change');
		}

        var users = $('.usersList :checked').parent();
		if(!$('#id_ocl').is(':checked') && users_plus.length > 0 && show_ocl_warn) {
			$.each(users_plus, function(index) {
				usr_list += ($(this).find('label').text() || $(this).text()) + '; ';
				if (index%5) usr_list += '<br />';
			});
			app.helpers.window(t.SYSTEM_MESSAGE, t.ASS_NOTIFY_OCL_WARN + usr_list,  [{
                text: t.SAVE,
                events: [{
                    name: 'click',
                    handler: function(e) {
                        $.nmTop().close();
                        save_assignment();
                        return false;
                    }
                }]
            },{
                text: t.CANCEL,
                events: [{
                    name: 'click',
                    handler: function(e) {
                        $.nmTop().close();
                        return false;
                    }
                }]
            }], null);
		} else if (!app.data.changed) {
            app.helpers.window(t.SYSTEM_MESSAGE, t.ASS_NO_CHANGES_ERR,
                               [{
                                text: t.OK,
                                events: [{
                                    name: 'click',
                                    handler: function() {
                                        $.nmTop().close();
                                        return false;
                                    }
                                }]
                               }]
                              )
        } else if (users.length<1 && parseInt($('#type_group').val())) {
            console.log($('#type_group').val());
            app.helpers.window(t.SYSTEM_MESSAGE, t.ASS_NO_USERS_ERR,
                               [{
                                text: t.OK,
                                events: [{
                                    name: 'click',
                                    handler: function() {
                                        $.nmTop().close();
                                        return false;
                                    }
                                }]
                               }]
                              )

        } else {
            save_assignment();
        }
	});

   $('a.close').click(function(){
       if(app.data.changed==true) {
           app.helpers.window(t.SYSTEM_MESSAGE, t.LEAVE_WITHOUT_SAVE, [{
              'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function() {
                       $.nmTop().close();
                       window.location = $('a.close').attr('href');
                       return true;
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
           false);
       } else {
           window.location = $('a.close').attr('href');
       }
       return false;
   });
   $('#addGroup').click(function(){
     app.helpers.throbber($('#groupsWrapper'));
     if($('#groups').val() != -1){
     	var className = 'even';
       if($('#groups option:selected').attr('disabled') !== true){
       	if($('#group_list li:last')){
       		className = $('#group_list li:last').hasClass('even') ? 'odd' : 'even';
       	}
        app.ma.createGroup($('#groups').val(), className);
       }
     }else{
       $('#groups option:enabled').each(function(i){
         if($(this).attr('value') != -1){
            app.ma.createGroup($(this).attr('value'), i%2 ? 'odd' : 'even');
         }
       });
     }
     $('.dotsWrapper').each(function() {
     	if($(this).find('.dot').length < 8) {
     		$(this).siblings('.browse').find('img').hide();
     	} else {
     		$(this).siblings('.browse').find('img').show();
     	}
     });
     app.helpers.throbber($('#groupsWrapper'), 'remove');
   });
   $('.previewBtn').live('click', function(e){
       e.preventDefault();
	   $('#modulesWrapper').hide();
	   $('#moduleDetailsWrapper .previewContent').html('');
	   $('#moduleDetailsWrapper').toggleClass('hidden', false);
	   $('#moduleDetailsWrapper .previewContent').append(
	       app.elements.getObj(
	         new app.elements.courseDetails(
	           app.data.map[$(this).closest('li').attr('id')]
	         )
	       )
	   );
   });
   $('.previewBackContainer a').live('click', function(e){
       e.preventDefault();
	   $('#modulesWrapper').show();
	   $('#moduleDetailsWrapper').toggleClass('hidden', true);	   
   });
   //$('#modulesWrapper li.first').next().css('left', $('#modulesWrapper li.first').width()-14);
   $('.tabs a').click(function(){
		/*$('ul.result').hide();
		$('#modulesWrapper li').removeClass('active');
		$(this).parent().addClass('active');
		$($(this).attr('href')).fadeIn('200');*/
		return false;
  	});
	$('.preview').live('click', function(event){
		event.preventDefault();
		var id = $(this).parent().children().first().attr('id'),
			bg = $('<div class="modalBg"></div>'),
			appConfig = app.config;
			mplayer = $('<div class="mplayerWrapper"><a href="javascript:void(0);" class="closeFW"></a><div id="video"></div></div>');
        bg.css({
            height: $(window).height(),
            width: $(window).width()
        });
        mplayer.css({
            left: $(window).width() / 2 - 350,
            top: 10
        });
        bg.appendTo($('body'));
        mplayer.appendTo($('body'));
        bg.click(function(){
        	mplayer.remove();
            $(this).unbind('click').remove();
        });
		$('.mplayerWrapper .closeFW').click(function(){
			mplayer.remove();
			bg.unbind('click').remove();
		});
        playerParams = {
        		'contentURL': '/content/modules/' + app.data.map[id].id + '/?format=json',
                'cType': 'playlist',
                'relativeURL': appConfig.mediaURL,
                'playingIndex': 0,
        	    'siteLanguage'	  : siteLanguage
            }
        
        if (app.config.player.mode == "html5") {
        	app.player.trackUser = false;
        	app.player.spawnHTML5(appConfig.player.modalSize, playerParams, 'opaque');
        } else {
        	playerParams.relativeURL = mediaURL;
        	playerParams.contentURL = '/content/modules/' + app.data.map[id].id + '/?format=xml';
        	app.player.spawnFlash('video', appConfig.player.modalSize, playerParams, 'opaque');        	
        }
	});

	// custom selectboxes
	$(".selectBoxJs").sb();
	$("#id_language").sb();
    $("#id_owner").sb();

	// search
    
    $('#showAdvanced').click(function(){
    	if ($('#modulesWrapper .search li:not(.always)').hasClass('hidden')) {
        	$('#modulesWrapper .search li:not(.always)').toggleClass('hidden', false);
        	$('#showAdvanced').html(t.HIDE_ADVANCED_SEARCH);
    	} else {
        	$('#modulesWrapper .search li:not(.always)').toggleClass('hidden', true);
        	$('#showAdvanced').html(t.SHOW_ADVANCED_SEARCH);
    	}
    });

    $('#search').keyup(function(){
        app.data.search_changed = true;
        showModules();
    });

    $('#id_language,#id_groups').change(function() {
        showModules();
    });

    var shouldBeHidden = function(listItem) {
        var groups = $.parseJSON($(listItem).parent().find('input.groups').val()),
        	selected_group_id = $.trim($('#id_groups :selected').val().toLowerCase());
        	ownerid = $(listItem).parent().find('.ownerid').val();
		checkSearch();
		if (!parseInt($('#type_group').val()) && $.inArray(parseInt(selectedGroup), groups) < 0) return true;
        if (document.location.hash == "#myModules") {
            if ($('#id_owner').val() && $('#id_owner').val() != ownerid) {
                return true;
            }
        } else {
            if ($('#id_owner').val() && (!haveAtLeastOneCommonGroupId(groups, app.data.user_groups) || $('#id_owner').val() == ownerid)) {
                return true;
            }
        }

        if(app.data.search_changed &&
        		$(listItem).html().toLowerCase().indexOf($.trim($('#search').val().toLowerCase())) == -1 &&
            	( $(listItem).siblings(".moduleAuthor").html().toLowerCase().indexOf($.trim($('#search').val().toLowerCase())) == -1 )) {
            return true;
        }

        if ($('#id_language').val() != "0" && $('#id_language').val() != $(listItem).attr('lang')) {
            return true;
        }

        if ($('#id_groups').val() != "0" && groups.indexOf(parseInt(selected_group_id)) == -1) {
            return true;
        }

        return false;
    }

    var showModules = function() {
        $('.moduleName').each(function() {
            $(this).parents('li').show();
        });
        
        $('.moduleName').each(function() {
            if (shouldBeHidden(this)){
                $(this).parent('li').hide();
            } else {
                $(this).parents('li').show();
            }
        });
    }

    var showOwnersGroups = function(owners_groups) {
    	var groupsSwitch = $('ul.groupsList').html();
    	
    	if (!$('#showMy').is(':checked')) return;
        $("#id_groups").html($("#id_groups_all").html());

        $("#id_groups").find("option").each(function(index, option) {
            var optionValue = parseInt($(option).attr("value"));
            if ($(option).attr("value") != 0 && !($(option).attr("value") in owners_groups)) {
                $(option).remove();
            }
        });
        $("ul.groupsList").find("li").each(function(index, item) {
            var itemValue = $(item).find('span').attr('id');
            itemValue = parseInt(itemValue.substring(itemValue.lastIndexOf('_') + 1));
            if (itemValue != 0 && itemValue != -2 && !(itemValue in owners_groups)) {
                if ($(item).next().length){
                    if (!index%2){
                        $(item).next().toggleClass('odd', false);
                        $(item).next().toggleClass('even', true);
                    } else {
                        $(item).next().toggleClass('odd', true);
                        $(item).next().toggleClass('even', false);
                    }                	
                }
                $(item).hide();
            }
        });

        $("#id_groups").sb('refresh');
    }

    $('#id_owner').change(function() {
        if (!$('#id_owner').val()) {
            $("#id_groups").html($("#id_groups_all").html());
            $("#id_groups").sb('refresh');
            return;
        }

        if (document.location.hash == "#myModules" || !document.location.hash) {
            $('.moduleAuthor').each(function() {
                if ($('#id_owner').val() != $(this).attr('ownerid')) {
                    $(this).parent('li').hide();
                } else {
                    $(this).parents('li').show();
                }
            });

            $.ajax({
                url: '/management/users/' + $('#id_owner').val() + "/groups/",
                type: 'GET',
                async: false,
                success: function(data, status, xhr) {
                    if (typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }
                    app.data.user_groups = data;
    
                    showOwnersGroups(data);
                    $('#modulesWrapper:not(.hidden) ul.result:not(.hidden)').trigger('loaded');
                }
            });
        } else {
            $.ajax({
                url: '/management/users/' + $('#id_owner').val() + "/groups/",
                type: 'GET',
                async: false,
                success: function(data, status, xhr) {
                    if (typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }
                    app.data.user_groups = data;
    
                    $('.moduleAuthor').each(function() {
                        var groups = $.parseJSON($(this).parent().find('input.groups').val()),
                            ownerid = $(this).parent().find('input.ownerid').val();
                        if ($('#id_owner').val() && (!haveAtLeastOneCommonGroupId(groups, data) || $('#id_owner').val() == ownerid)) {
                            $(this).parent('li').hide();
                        } else {
                            $(this).parent('li').show();
                        }
                    });
    
                    showOwnersGroups(data);
                    $('#modulesWrapper:not(.hidden) ul.result:not(.hidden)').trigger('loaded');
                }
            });
        }
    });

    var haveAtLeastOneCommonGroupId = function(groupArray, groupDict) {
        for(var i = 0; i < groupArray.length; i++) {
            for(key in groupDict) {
                if(groupArray[i] == parseInt(key)) {
                    return true;
                }
            }
        }

        return false;
    }

    var flip = function(from, to) {
        var tmp = $(from).html();
        $(from).html($(to).html());
        $(to).html(tmp);
        $(from).sb('refresh');
        $(from).change();
    };

    $('#showMy').live('change', function() {
    	var groupsSwitch = $('ul.groupsList').html();
        flip('#groups', '#my_groups');
        flip('#id_groups', '#id_groups_all');
        $('ul.groupsList').html($('ul.allGroupsList').html());
        $('ul.allGroupsList').html(groupsSwitch);
    });
    $('#showMy').attr('checked', true);
    // Set active tab

    $("a[href='"+document.location.hash+"']").parent().addClass("active");

    $("a[href='#allModules']").click(function(){
    	$(this).parent().addClass("active");
    	$(this).parent().siblings("li").removeClass("active");
    	$("ul.allModules").html(" ");
    	window.location.hash = "allModules";
    	$("ul.myModules").addClass("hidden");
    	$("ul.allModules").removeClass("hidden");
    	app.ma.loadActiveModules(document.location.hash.replace(/#/, ''));
    	return false;
    })
    $("a[href='#myModules']").click(function(){
    	$(this).parent().addClass("active");
    	$(this).parent().siblings("li").removeClass("active");
    	$("ul.myModules").html(" ");
    	$("ul.allModules").addClass("hidden");
    	$("ul.myModules").removeClass("hidden");
    	window.location.hash = "myModules";
    	app.ma.loadActiveModules(document.location.hash.replace(/#/, ''));
    	return false;
    })

    // -- overlays
    $('.dotsWrapper .movableDot').live('mouseover', function(){
      clearTimeout(tim[$(this).attr('id')]);
      if($(this).find('.close_overlay').length == 0){
          var overlay = $('<a class="close_overlay" title="' + t.ITEM_REMOVE + '"></a>');
          overlay.css({
            'left': $(this).position().left + $(this).outerWidth() - 8,
            'top': $(this).position().top
          });
          $(this).find('span').addClass('hover');
          overlay.appendTo($(this));
      }
    }).live('mouseout', function(){
        var that = this;
        tim[$(this).attr('id')] = setTimeout(function(){
            $(that).find('span').removeClass('hover');
            $('.close_overlay').remove();
        }, 50);
    });
    $('.close_overlay, .movableDot span').live('mouseover', function(){
        clearTimeout(tim[$(this).parent().attr('id')]);
    });
    $('.close_overlay').live('mouseout', function(){
        var that = this;
        tim[$(this).parent().attr('id')] = setTimeout(function(){
            $(that).siblings('span').removeClass('hover');
            $('.close_overlay').remove();
        }, 50);
    }).live('click', function(){
      var grp = app.data.map[$(this).parents('li').attr('id')].id;
      var mod = app.data.map[$(this).parents('.movableDot').attr('id')].id;
      delete(app.data.assignments[grp][mod]);
      $(this).parents('.movableDot').remove();
      app.data.changed = true;
   	  $('.dotsWrapper').each(function() {
     	if($(this).find('.dot').length < 8) {
     		$(this).siblings('.browse').find('img').hide();
     	} else {
     		$(this).siblings('.browse').find('img').show();
     	}
      })
      return false;
    });

    searchDefault = $('#search').val();
    $('#search').focus(function() {
    	if(searchDefault == $('#search').val()) {
    		$('#search').val('');
    	}
    });
    $('#search').blur(function() {
    	if($('#search').val() == '') {
    		$('#search').val(searchDefault);
    		app.data.search_changed = false;
    	}
    });
    $('#id_ocl').live("change", function() {
        var handle_ocl = function() {
            if( $("#id_ocl").is(':checked')) {
                $('#allow_login').attr('style', '');
                $('#allow_login').next().attr('style', '');
                $('#id_ocl_expires_on').parent().attr('style', '');
            } else {
                $('#allow_login').attr('style', 'display: none;');
                $('#allow_login').next().attr('style', 'display: none;');
                $('#id_ocl_expires_on').parent().attr('style', 'display: none;');
            }
        };
        var type = getTemplateType();

        if (app.data.savedTemplate) {
            if (type !== app.data.savedTemplate.type) {
                app.helpers.window(t.EMAIL_TEMPLATE, t.EMAIL_TEMPLATE_MSG, [
                    {
                        text: t.YES,
                        events: [{
                            name: 'click',
                            handler: function (e) {
                                e.preventDefault();
                                handle_ocl();
                                $.nmTop().close();
                                $(this).parents('div').remove();
                                return true;
                            }
                        }]
                    },
                    {
                        text: t.NO,
                        events: [{
                            name: 'click',
                            handler: function(e){
                                e.preventDefault();
                                $('#id_ocl').attr('checked', !$('#id_ocl').is(':checked'))
                                $.nmTop().close();
                                $(this).parents('div').remove();
                                return true
                            }
                        }]
                    }
                ], null);
                return true;
            }
        }
        handle_ocl();
    });
    $('#id_ocl').trigger('change');
});

var searchDefault;
function checkSearch(){
    clearTimeout(searchTimer);
    searchTimer = setTimeout("if ( $('#search').val() == searchDefault ) { $('#search').val(''); app.data.search_changed = false; }", 300);
}
