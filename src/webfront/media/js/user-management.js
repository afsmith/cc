var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    $('select').html('');
    app.gm.loadData();
    app.data.reload = false;

      app.listeners.groupChangeListener();
      app.listeners.groupFilterListener();
      app.listeners.groupMoveUsersListener();
      app.listeners.groupRemoveUsersListener();
      app.listeners.groupUserSelectedListener();
      app.listeners.toggleUserGroupManagerListener();
      app.listeners.enableGroupsSelfRegisterListener();
      app.listeners.disableGroupsSelfRegisterListener();

      function backup() {
        $('#userlist_backup').html($('#userlist').html());
        $('#grouplist_backup').html($('#grouplist').html());
      }

      $('#groups, #my_groups').change(function(){
				if ($(this).attr('id') == 'groups') {
						list = 'grouplist';
				} else {
						list = 'userlist';
				}

				if ( ( list == 'grouplist' && $("#allGroups .selectbox div.text:visible").text() == $('#groups option:selected').text() ) || ( list == 'userlist' && $("#myGroups .selectbox div.text:visible").text() == $('#my_groups option:selected').text() ) ) {

						var backup_name = list + '_backup';

						$('#' + backup_name).remove();
						app.triggerEvent('groupListChange', $(this).attr('id'));

						var backup = $('<select>').attr('id',backup_name).attr('name',backup_name).hide();
						$(backup).html($('#' + list).html());

						$('#' + list).parent().append(backup);
				}
      });
      $('#move_users').click(function(e){
        app.triggerEvent('usersMoved');
   		backup();

      });
      $('#narrow, #narrow2').keyup(function(){
      	var list;
      	if ($(this).attr('id') == 'narrow2') {
      		list = 'userlist';
      	} else {
      		list = 'grouplist';
      	}
      	$('#' + list).html('');
      	$('#' + list).html($('#' + list + '_backup').html());
        app.triggerEvent('groupFiltered', $(this).attr('id'));
      });
      $('#rs').live('click', function(){
        app.triggerEvent('groupRemoveUsers');
        backup();
        return false;
      });
      $('#tm').live('click', function(){
        app.triggerEvent('toggleUserGroupManager');
        return false;
      });
      $('#userlist, #grouplist').change(function(){
        app.triggerEvent('userSelected', $(this).attr('id'));
      });
      $('.nyroModalClose').live('click', function(){
        if($.nmTop()){
          $.nmTop().close();
        }
        return false;
      });

      $('#showMy').change(function() {
        var tmp = $('#my_groups').html();
        $('#my_groups').html($('#my_groups_tmp').html());
        $('#my_groups_tmp').html(tmp);
        $("#my_groups").sb('refresh');
        $('#my_groups').change();
        $('#userlist').html('');
      });

      $('#showMy').attr('checked', true);


      $('#nga').click(function(){
        //app.triggerEvent('groupAdd');
        var cnf = app.config.modal;
        $.nmManual(
          '/management/groups/create/'
        );
        return false;
      });
      $('#ge').live('click', function(){
        if($('#my_groups').val() != 0){
          var cnf = app.config.modal;
          $.nmManual(
            '/management/groups/' + $('#my_groups').val() + '/'
          );
        }
        return false;
      });
      $('#gr').live('click', function(){
        if($('#my_groups').val() != 0){
          /*if(app.data.memberships[$('#my_groups').val()].length > 0){
            app.helpers.window(t.SYSTEM_MESSAGE, t.REMOVED_GROUP_EMPTY);
          }else{*/
              app.helpers.window(
                   t.SYSTEM_MESSAGE,
                   t.GROUP_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
                   [{
                       'text': t.YES,
                       events: [{
                           name: 'click',
                           handler: function(){
                               $.post(
                                 '/management/groups/' + $('#my_groups').val() + '/delete/',
                                 '',
                                 function(data, status, xmlHttpRequest){
                                      app.gm.loadData();
                                      $('#u_details_content').html(t.NO_USER_SELECTED);
                                      $('#userlist').html('');
                                      app.helpers.window(t.SYSTEM_MESSAGE, t.GROUP_REMOVED);
                                });
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
         //}
        }
        return false;
      });
      $("#ure").live('click', function() {
        $.nmManual(
            '/management/users/delete/',{
            	callbacks: {
            		'beforeShowCont': function() {
            			$('#id_send_goodbye_email').closest('li').append(
            					'<div id="previewMessageBtn" class="remove"></div>');
            			$('#id_send_goodbye_email').unbind();
            			if (!$('#id_send_goodbye_email').is(':checked')) $('#previewMessageBtn').hide();
            			$('#id_send_goodbye_email').change(function(){
            				if ($('#id_send_goodbye_email').is(':checked')) {
            					$('#previewMessageBtn').show()
            				} else $('#previewMessageBtn').hide();
            			});
            		}
            	}
            }
        );
      });
      $('#gex').live('click', function(){
        if($('#my_groups').val() != 0){
          if($('#userlist option').length > 0){
            window.open('/management/groups/' + $('#my_groups').val() + '/members/export/');
          }else{
            app.helpers.window(t.SYSTEM_MESSAGE, t.NO_USERS_EXPORT);
          }
        }else{
          app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_GROUP_EXPORT);
        }
        return false;
      });
      $('#gim').live('click', function(){
        if($('#my_groups').val() != '0'){
            $.nmManual(
                '/management/groups/' + $('#my_groups').val() + '/members/import/',
                {
                	callbacks: {
		              'beforeHideCont': function(){
		                  if(app.data.reload) {
		                      app.data.reload = false;
		                      parent.location.reload();
		                  }
		              }
		           }
                }
            );
        }else{
          app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_GROUP_IMPORT);
        }
        return false;
      });

      $('#ru_yes').live('click', function(){
        var userId = Ing.findInDOM().data.activeUser.id;
        var deleteUser = function(sendGoodbyeEmail) {
            $.post('/management/users/' + userId + '/delete/?send_goodbye_email=' + sendGoodbyeEmail, '',
                    function(data, status, xmlHttpRequest){
                        app.gm.saveState();
                        app.gm.loadData();
                        $('#u_details_content').html(t.NO_USER_SELECTED);
                        app.helpers.window(t.SYSTEM_MESSAGE, t.USER_REMOVED);
                    });
            $.nmTop().close();
            return false;
        };

        notification_input = $(this).parent().prev().find("#id_send_email")
        deleteUser(notification_input.is(":checked"));
        return false;
      });
      
      $('#previewMessageBtn').live('click', function(){
    	action = $(this).attr('class') + '_user';
		$.post('/messages/preview/', JSON.stringify({action: action}), function(data) {
			var bg = $('<div class="modalBg customModalBg onTop"></div>'),
				modal = $(data);
		        messageTemplate = '',
	        	iframe = '';
		        
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
		    $(modal).addClass('onTop');
		    messageTemplate = app.helpers.htmlSpecialDecoder($('#messageTemplate').html());
		    $('a.customModalCloseButton').click(function(){
		    	$('#assignmentPreview').animate({
		    	    opacity: 0,
		    	  }, 300, function() {
		    		$('#assignmentPreview').remove();
		    		$('.customModalBg').animate({
		        	    opacity: 0,
		      	  	}, 300, function() {
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
		      			$('iframe').contents().find('html').html(messageTemplate);
		    	        $('#messageTemplate').remove();
		      		});     	  		
			  	});
		}, 'html');
      });

      $('#ru_no').live('click', function(){
        $.nmTop().close();
        return false;
      });

      $('#ru').live('click', function(){
        var cnf = app.config;
        var userId = Ing.findInDOM().data.activeUser.id;
        if(userId){
            $.nmManual(
            '/management/users/' + userId + '/delete/',
            {
                sizes: {
                w: cnf.width,
                h: cnf.height
                }
            }
            );
           return false;
        }else{
          app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_USER_REMOVE);
        }
        return false;
      });
      $('#eu').live('click', function(){
        var userId = Ing.findInDOM().data.activeUser.id;
        var cnf = app.config.modal;
        $.nmFilters({
          afterShowCont: {
            is: function(nm){ return true},
            filledContent: function(nm){
              $('#newUserForm select').sb();
              $('#id_group').val($('#my_groups').val());
            }
          }
        });
        $.nmManual(
          '/management/users/' + userId + '/',
          {
            sizes: {
              w: cnf.width,
              h: cnf.height
            }
          }
        );
        return false;
      });
      $('#du').live('click', function(){
        var cnf = app.config;
        var userId = Ing.findInDOM().data.activeUser.id;
        if(userId){
          $.post(
           '/management/users/' + userId + '/deactivate/',
           '',
           function(data, status, xmlHttpRequest){
            app.gm.saveState();
            app.gm.loadData();
            $('#u_details_content').html(t.NO_USER_SELECTED);
            app.helpers.window(t.SYSTEM_MESSAGE, t.USER_DEACTIVATED);
           });
           return false;
        }
        return false;
      });
      $('#au').live('click', function(){
        var cnf = app.config;
        var userId = Ing.findInDOM().data.activeUser.id;
        if(userId){
          $.post(
           '/management/users/' + userId + '/activate/',
           '',
           function(data, status, xmlHttpRequest){
            app.gm.saveState();
            app.gm.loadData();
            $('#u_details_content').html(t.NO_USER_SELECTED);
            app.helpers.window(t.SYSTEM_MESSAGE, t.USER_ACTIVATED);
           });
           return false;
        }
        return false;
      });
      $('#anu').live('click', function(){
        if($('#my_groups').val() != 0){
          var cnf = app.config.modal;
          $.nmFilters({
            afterShowCont: {
              is: function(nm){ return true},
              filledContent: function(nm){
                $('#newUserForm select').sb();
                $('#id_group').val($('#my_groups').val());
                $('#name_group').text($('#my_groups :selected').text());
                $('ul.selectbox').css("width","auto");
              }
            }
          });
          $.nmManual(
            '/management/users/create/', {
				resizable: true
            });
        }else{
          app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_GROUP_ADD);
        }
        return false;
      });
      $('#rp').live('click', function(){
        var cnf = app.config;
        var userId = Ing.findInDOM().data.activeUser.id;
        if(userId){
          $.post(
           '/management/users/' + userId + '/reset_pass/',
           '',
           function(data, status, xmlHttpRequest){
            app.gm.saveState();
            app.gm.loadData();
            $('#u_details_content').html(t.NO_USER_SELECTED);
            $('#reset_message').html(t.USER_PASSWORD_RESET);
            //app.helpers.window(t.SYSTEM_MESSAGE, t.USER_PASSWORD_RESET);
           });
           return false;
        }
        return false;
      });
      $('#newGroupForm a, #newUserForm #sb, #importCSVForm a').live('click', function(event){
        $(this).parents('form').submit();
        return false;
      });
      $('#newGroupForm').live('submit', function(){
        $.post(
           $(this).attr('action'),
           $(this).serialize(),
           function(data, status, xmlHttpRequest) {
              if(xmlHttpRequest.status == 201){
                data = $.parseJSON(data);
                $('.nyroModalClose').trigger('click');
                app.gm.saveState({
                    'groups': $('#groups').val(),
                    'my_groups': data.id
                });
                $('#my_groups_tmp').html("");
                app.gm.loadData();
                $('#showMy').attr('checked', true);
              }else{
                $('.nyroModalLink').html(data);
              }
           });
           return false;
        });
      $('#newUserForm').live('submit', function(){
        $.post(
           $(this).attr('action'),
           $(this).serialize(),
           function(data, status, xmlHttpRequest){
              if(xmlHttpRequest.status == 201){
                $.nmTop().close();
                var groupId = $('#my_groups').val();
                if(groupId == 0){
                  app.gm.saveState();
                  app.gm.loadData();
                  return false;
                }else{
                  if(data){
                    if(typeof data != 'object'){ // IE bug --
                      data = $.parseJSON(data);
                    }
                    var userId = data.id;
                    var data = {'action': 'add', members: [userId]};
                    var users = Ing.findInDOM().data.memberships;
                    Ing.findInDOM().helpers.throbber($('#userlistWrapper'));
                    $.post(
                      '/management/groups/' + groupId + '/members/',
                      JSON.stringify(data),
                      function(data){
                        if(typeof data != 'object'){ // IE bug --
                          data = $.parseJSON(data);
                        }
                        if(data.status == 'OK'){
                          $('#my_groups_tmp').html("");
                          app.gm.saveState();
                          app.gm.loadData();
                          $('#showMy').attr('checked', true);
                        }else{
                          // -- tutaj obsulzyc blad dodawania
                        }
                        Ing.findInDOM().helpers.throbber($('#userlistWrapper'), 'remove');
                    });
                  }else{
                    $('#my_groups_tmp').html("");
                    app.gm.saveState();
                    app.gm.loadData(true, true);
                    //$('#showMy').attr('checked', true);
                    return false;
                  }
                }
              }else{
                $('.nyroModalLink').html(data);
              }
              $('#newUserForm select').sb();
              // Safari fix
              $('ul.selectbox').css("width","auto");
              // $.nmTop().resize(true);
           });
           return false;
        });
    $('#enable_self_register').live('click', function(){
        app.triggerEvent('enableGroupsSelfRegister');
        return false;
    });
    $('#disable_self_register').live('click', function(){
        app.triggerEvent('disableGroupsSelfRegister');
        return false;
    });
    
    $('#id_send_email').live('change', function(){
    	if ($('#id_send_goodbye_email').length) return; 
    	if ($(this).is(':checked')) {$('#previewMessageBtn').show()} else $('#previewMessageBtn').hide();
    });

	$('#grouplist').bind('focus',function() {
		$(this).parent().parent().siblings('.rightArrow').addClass('active')});
	$('#grouplist').bind('blur',function() {
		$(this).parent().parent().siblings('.rightArrow').removeClass('active')});
	$('#userlist').bind('focus',function() {
		$('#rs').addClass('active')});
	$('#userlist').bind('blur',function() {
		$('#rs').removeClass('active')});
	

	$('#self_register_group_list').bind('focus',function() {
		$('#disable_self_register').addClass('active')});
	$('#self_register_group_list').bind('blur',function() {
		$('#disable_self_register').removeClass('active')});
    $('#all_group_list').bind('focus',function() {
		$('#enable_self_register').addClass('active')});
	$('#all_group_list').bind('blur',function() {
		$('#enable_self_register').removeClass('active')});

		var searchDefault = $('#narrow').val();
		$('#narrow').focus(function() {
			if(searchDefault == $('#narrow').val()) {
				$('#narrow').val('');
			}
		});
		$('#narrow').blur(function() {
			if($('#narrow').val() == '') {
				$('#narrow').val(searchDefault);
			}
		});
		var searchDefault = $('#narrow2').val();
		$('#narrow2').focus(function() {
			if(searchDefault == $('#narrow2').val()) {
				$('#narrow2').val('');
			}
		});
		$('#narrow2').blur(function() {
			if($('#narrow2').val() == '') {
				$('#narrow2').val(searchDefault);
			}
		});
    $('#id_role').live('change', function(){
        console.log('dddddddddddd');
        if ($(this).val() == 40){
            $('#newUserForm input#id_send_email').removeAttr('checked');
            $('#previewMessageBtn').hide();
        } else {
            $('#newUserForm input#id_send_email').attr('checked', 'checked');
            $('#previewMessageBtn').show();
        }
    });
});
