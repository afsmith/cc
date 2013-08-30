var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    $.ajaxSetup({
		error : function(x) {
			$("body").html(x.responseText);
		}
	});
    $(app).bind('msgformOpened', function(){
        $('.wrote textarea').attr('disabled', 'disabled');
        $('.textarea textarea:enabled').html('');
    });

    $('#messages li').live('click', function(){
				if ($(this).attr("id")) {
                        var href = "/messages/view/" + $(this).attr("id") + "/";
                        if ($(this).hasClass('ocl')) {
                            href = href + "?ocl=true";
                        }
						$.get(href, function(data) {
                            $("#selectedMessage").html(data.replace(/&amp;/gi, '&'));
                            if($( "#datepicker" ).length) {
                                $( "#datepicker" ).datepicker({
                                    showOn: "button",
                                    buttonImage: mediaURL + "img/blank.gif",
                                    buttonImageOnly: true,
                                    dateFormat: 'yy-mm-dd',
                                    minDate: 0
                                });
                                if($("#datepicker").val()=='') {
                                    $("#datepicker").val(t.DATE_NOT_SET);
                                }
                            }
						});
						$(this).siblings("li").removeClass("active");
						if ($("#messagesWrapper ul li:first").hasClass("active"))
							$(this).removeClass("unread").addClass("active").find(".icoNew").hide();
						else
							$(this).addClass("active");
				}
    });

    $('#removeMessages').live('click', function(){
        var href = $(this).attr('href');
        var messages_id = [];
        $('.messageToRemove:checked').each(function() {
            messages_id.push($(this).val());
        });
 
        if(messages_id.length > 0) {
            app.helpers.window(
               t.SYSTEM_MESSAGE,
               t.MSG_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
               [{
                   'text': t.YES,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.nmTop().close();
                               var data = {
                                   "messages": messages_id
                               };
                               $.post(href, JSON.stringify(data),function(data){
                                    if(data.status == "OK") {
                                        location.reload(true);
                                    } else {
                                        app.helpers.window(t.SYSTEM_MESSAGE,
                                            t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["error"]);
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
    $('#replyMessage').live('click', function(){
        app.callbacks.openReply($(this).attr("sendername"), $(this).attr("senderid"), $(this).attr("messageid"));
    });
    
    $('#resendMessage').live('click', function(){
       $.get($(this).attr('href'), function(data){
            if(data.status == "OK") {
                app.helpers.window(t.SYSTEM_MESSAGE, "Message was resent");
            } else {
                app.helpers.window(t.SYSTEM_MESSAGE, data.error);
            }
        });
       return false;

    });
    
    $('#selectAllMessages').live('click', function(){
        if($('.messageToRemove:first').is(":checked")) {
            $('.messageToRemove').each(function() {
                $(this).removeAttr("checked");
            });
        } else {
            $('.messageToRemove').each(function() {
                $(this).attr("checked", "checked");
            });
        }
    });

    $('#removeMessage').live('click', function(){
        var href = $(this).attr('href');
        app.helpers.window(
           t.SYSTEM_MESSAGE,
           t.MSG_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.nmTop().close();
                       $.post(href, function(data){
                            if(data.status == "OK") {
                                location.reload(true);
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
       return false;
    });
    
    $('#oclExpireNow').live('click', function(){
        var href = $(this).attr('href');
 
        app.helpers.window(
           t.SYSTEM_MESSAGE,
           t.OCL_EXPIRE_CONFIRMATION+'<br />',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.nmTop().close();
                           $.post(href, function(data){
                                if(data.status == "OK") {
                                    location.reload(true);
                                } else {
                                    app.helpers.window(t.SYSTEM_MESSAGE,
                                        t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["error"]);
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
       return false;
    });
    $('#setExpirationDate').live('click', function(){
       var href = $(this).attr('href');
       $.post(href, {"expires_on": $('#datepicker').val()}, function(data){
            if(data.status == "OK") {
                if (data.expired) {
                    location.reload(true);
                } else {
                    app.helpers.window(t.SYSTEM_MESSAGE, t.OCL_EXPIRE_UPDATE_DONE);
                }
            } else {
                app.helpers.window(t.SYSTEM_MESSAGE,
                    t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["error"]);
            }
            return false;
        });
        return false;
    });

    $('#messageFilter').live('change', function(){ reloadMessages(); });
    $('#show_my_ocl_links').live('change', function(){ reloadMessages(); });
    $('#ocl_messages_only').live('change', function() { reloadMessages(); });
    if($('#ocl_messages_only').is(":checked")) { $('#removeMultipleMessageButtons').hide(); }
    
    $('#messagesWrapper .tabs li.outbox').css('left', $('#messagesWrapper .tabs li.inbox').width()-14);
    $('#messagesWrapper .tabs li.ocl').css('left', 
    		$('#messagesWrapper .tabs li.inbox').width() + $('#messagesWrapper .tabs li.outbox').width() -28);

    $('#messages li:first-child').trigger('click');
    $('#messageFilter').sb();

    function reloadMessages() {
        var href = $('#messageFilter').attr('path') + "?course_id="+$('#messageFilter').val();
        if($('#ocl_messages_only').length > 0) {
            href = href+"&ocl_only="+$('#ocl_messages_only').is(":checked");
        }
        if($('#show_my_ocl_links').length > 0){
            href = href+"&show_my_ocl_links="+$('#show_my_ocl_links').is(":checked");
        }
        window.location = href;
    }
});
