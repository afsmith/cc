$(function () {
    $.ajaxSetup({
    	error: function(x) {
    	    $("body").html(x.responseText);
    	}});
    
    var savedMsg = '<div class="admSettingsSaved modalContent"><span>' + t.SETTING_SAVED + '</span></div>';
    
    CKEDITOR.config.image_previewText = " ";
    CKEDITOR.config.contentsCss = "/media/css/contentsCKE.css";
    
    CKEDITOR.on('instanceReady', function (event) {
		event.editor.document.on('drop', function (event) {
			event.data.preventDefault(true);
		});
	});
    
    $("#selectMessageTemplate").live('change', function() {
    	var id = $(this).val();
    	$(".messageContent").hide();
    	$(".messageTitle").hide();
    	$(".messageDescription").hide();
    	$(".messageSend").hide();
    	$(".messageAsDefault").hide();
    	$("#messageTemplateSubject-" + id).show();
    	$("#messageTemplate-"+ id).show();
    	$("#messageTemplateSend-"+ id).show();
    	$("#messageDescription-" + id).show();
    	$("#messageSaveAsDefault-" + id).show();
    });

    $('#MessagesTemplateForm .button-default').live('click', function() {
    	var id = $("#selectMessageTemplate").val();
    	var defaultText = $('#messageTemplate-' + id + ' input[type="hidden"]').val();
        var defaultSubject = $('#messageTemplateSubject-' + id + ' input[type="hidden"]').val();
    	$('#messageTemplateSubject-' + id + ' input[type="text"]').val(defaultSubject);
        $("#messageTemplate-"+ id + "* textarea").data("editor").setData(defaultText);

    	return false;
    });

    $('#MessagesTemplateForm .button-submit').live('click', function(ev) {
        ev.preventDefault();

    	var data = {
           'action': 'save',
           'user_edit': $("#userEdit").val(),
           'data': { }
        };

        $('#selectMessageTemplate option').each(function(id) {
            var exists = function(selector){
                return ($(selector).length > 0);
            }
        	var id = $(this).val();
        	var title = $('#messageTemplateSubject-' + id + ' input').val();
        	var text = $('#messageTemplate-' + id + ' * textarea').data("editor").getData();
                var save_as_default = $('#messageSaveAsDefault-' + id + ' input').attr('checked');
            var sendMsg = 'D';
            var sendMsg_field = '#messageTemplateSend-' + id + ' input';
            if(exists(sendMsg_field)){
                if($(sendMsg_field).attr('checked')){
                    sendMsg = 'T';
                }else{
                    sendMsg = 'F';
                }
            }

        	data.data[id] = {'title'  : title ,
                             'text'   : text,
                             'send_msg': sendMsg,
                             'save_as_default': save_as_default};
        });

		$.post(
			'/messages/templates/save/',
			JSON.stringify(data),
			function(data) {
				if(data.status == "OK") {
					if ($('#adm_toolsTab #selectedMessage').length) {
	                   $('#adm_toolsTab #selectedMessage').html(savedMsg);
	                   app.fitAdminTools();						
					} else {
						app.helpers.window(t.SYSTEM_MESSAGE, t.SETTING_SAVED, null, null, function() {
	                        window.location = "/messages/my_templates/";
	                    });
					}
			    }
		});

        return false;
    });

    $("#selectMessageTemplate").sb();
    $("#selectMessageTemplate").change();
    $("textarea").each(function (i) {
        var editor = CKEDITOR.replace(this, {"height": "66%", 
        									"resize_enabled": false,
        									"filebrowserUploadUrl": "/messages/upload-image/"});
        $(this).data("editor", editor);
    });
});
