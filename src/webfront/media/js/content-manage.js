var app = new Ing();
var ContentManage = {
    selectedGroupsIds: function() {
        var ids = [];
        $('#selectedGroupsList option').each(function(){
            ids.push($(this).val());
        });
        return ids;
    }
};

/**
  * Form handler
  */
var fh = {
    VALUE_POS: 0,
    HTML_POS: 1,
    
    allGroupsArr: [],
    
    init: function() {
        var isFilled = false,
            me = this,
            sgi ='';      
        
        // allow downloading
        if (!isEdited) {
            if (app.helpers.cookie.get("is_downloadable") === 'checked'){
                $("#id_is_downloadable").attr('checked', 'checked');
            } else {
                $("#id_is_downloadable").removeAttr('checked', 'checked');
                //isFilled = true;
            }
            sgi = app.helpers.cookie.get("selected_groups_ids").split(',');
        }
        
        // group rights
        this.initAllGroupsArr();  
        //var sgi = app.helpers.cookie.get("selected_groups_ids").split(',');
        
        if (sgi.length > 0) {
            $('#availableGroupsList').empty();
            $('#selectedGroupsList').empty();
            
            $.each(this.allGroupsArr, function(index, val) {
                var $el = sgi.indexOf(val[me.VALUE_POS]) !== -1 ? $('#selectedGroupsList') : $('#availableGroupsList');
                $el.append($('<option>', {value: val[me.VALUE_POS], text : val[me.HTML_POS]}));                
            });
        }
        
        // tags
        var tags = app.helpers.cookie.get("tags").split(',');
        if (tags.length > 1) {
            isFilled = true;
        
            $.each(tags, function(index, val) {
                $('#newTag').val($.trim(val));
                app.callbacks.handleTags('#newTag');
                app.data.changed = true;
                $('#newTag').blur().focus();
            });
        }
        
        // simple fields
        if (!isEdited) {
            this.initField("#id_language", app.helpers.cookie.get("language")) ?  isFilled = true : isFilled = isFilled;
            this.initField("#id_duration",app.helpers.cookie.get("duration")) ?  isFilled = true : isFilled = isFilled;
            this.initField("#datepicker", app.helpers.cookie.get("expires_on")) ?  isFilled = true : isFilled = isFilled;
            this.initField("#id_note",  app.helpers.cookie.get("note")) ?  isFilled = true : isFilled = isFilled;

            // delete after expire
            if (app.helpers.cookie.get("delete_after_expire") === 'checked'){
                $("#id_delete_expired").attr('checked', 'checked');
    //            isFilled = true;
            } else {
                $("#id_delete_expired").removeAttr('checked', 'checked');
            }
        }

        // activate Clear btn
        if (isFilled == true) {
            $('#mcc').removeClass('button-disabled');
        }
     },
     
     initAllGroupsArr: function() {
         $('#selectedGroupsList option').each(function(){
             var arr = new Array(2);
             arr[fh.VALUE_POS] = $(this).val();
             arr[fh.HTML_POS] = $(this).html();
             fh.allGroupsArr.push(arr);
        });
     },
     
     initField: function(field, value, setAsContent) {
         setAsContent = setAsContent || false;
         if (value.length > 0) {
             if (setAsContent == false) {
                 $(field).val(value);
             } else {
                 $(field).html(value);
             }
             return true;
         } else {
             return false;
         }
     },
        
     setContentCookie: function() {
        app.helpers.cookie.set("is_downloadable", $("#id_is_downloadable").is(":checked") ? 'checked' : '', app.config.cookieTime);
        app.helpers.cookie.set("selected_groups_ids", ContentManage.selectedGroupsIds(), app.config.cookieTime);
        app.helpers.cookie.set("tags", this.tagsToArr(), app.config.cookieTime);
        app.helpers.cookie.set("language", $("#id_language").val(), app.config.cookieTime);
        app.helpers.cookie.set("duration", $.trim($("#id_duration").val()), app.config.cookieTime);
        app.helpers.cookie.set("expires_on", $("#datepicker").val(), app.config.cookieTime);
        app.helpers.cookie.set("note", $("#id_note").val(), app.config.cookieTime);
        app.helpers.cookie.set("delete_after_expire", $("#id_delete_expired").is(":checked") ? 'checked' : '', app.config.cookieTime);
    },
    
    tagsToArr: function() {
        var arr = [];
        $('#tagList li').each(function(){
            var txt = $(this).text().split('<');
            arr.push(txt[0]);
        });
        return arr;
    },
    
    clear: function() {
        this.clearForm();
        this.clearCookie();
        $('#mcc').addClass('button-disabled');
    },
    
    clearForm: function() {
        $("#id_is_downloadable").attr('checked', 'checked');
        
        $('#availableGroupsList').empty();
        $('#selectedGroupsList').empty();
        $.each(this.allGroupsArr, function(index, val) {
            $('#availableGroupsList').append($('<option>', {value: val[fh.VALUE_POS], text : val[fh.HTML_POS]}))                
        });
        
        $('#tagList').empty();   
        $("#id_language").val('').sb('refresh');
        $("#id_duration").val('');
        $("#datepicker").val('');
        $("#id_note").val('');
        
        $("#id_delete_expired").removeAttr('checked', 'checked');
    },
    
    clearCookie: function() {
        var cookie = app.helpers.cookie,
            time = new Date().getTime() - 3600;
        $.each(['is_downloable', 'selected_groups_ids', 'tags', 'language', 'duration', 'expires_on', 'note', 'delete_after_expire'], function(key, value){
            cookie.set(value, '', time);
        });
    },
    
};

$(document).ready(function(){

    app.config.mediaURL = mediaURL;
    app.config.searchForm = false;
    app.config.tagsInput = '#newTag';
    app.data.tags = [];
    app.data.owner = $('#id_owner').val();
    app.data.changed = false;
    if($("#datepicker").val()=='') {
        $("#datepicker").val(t.DATE_NOT_SET);
    }
    
    app.run();
    
    $.ajaxSetup({
        error : function(x) {}
    });
	
    app.helpers.trimming($('#id_note'), 400, true);

    $('input[type=text],textarea,.selectBoxJs').change(function() {
        app.data.changed = true;
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

		$('a.closeFW').click(function(){
        $.nmTop().close();
    });

    $('#toSelectedGroups').click(function(e){
         $('#availableGroupsList option:selected').each(function(e, elem) {
            $(elem).appendTo($("#selectedGroupsList"));
         });
        app.data.changed=true;
    });

    $('#fromSelectedGroups').click(function(e){
        $('#selectedGroupsList option:selected').each(function(e, elem) {
            $(elem).appendTo($("#availableGroupsList"));
        });
        app.data.changed=true;
    });

	$('#availableGroupsList').bind('focus',function() {
		$(this).parent().siblings('.arrow').addClass('active')});
	$('#availableGroupsList').bind('blur',function() {
		$(this).parent().siblings('.arrow').removeClass('active')});
	$('#selectedGroupsList').bind('focus',function() {
		$(this).parent().siblings('.arrow').addClass('active')});
	$('#selectedGroupsList').bind('blur',function() {
		$(this).parent().siblings('.arrow').removeClass('active')});

    $('#uf').live('click', function(){
        $(this).parents('form').submit();
        return false;
    });

    $('.nyroModal').nyroModal({
        callbacks: {
            'beforeShowCont': function(){
                $("#dmsFiles").treeview({
			        url: "/content/dms/files/"
		        });
            }
        }
    });

    $('#mcc').live('click', function () {
        fh.clear();
    });

    $('#mcd').live('click', function(){
        var fileId = $("#id_file_id").val();
        if(fileId){
            var newTags = [];
            var oldTags = [];

            if(!$("#mct").val()) {
                //app.helpers.window(t.SYSTEM_MESSAGE, t.NAME_IS_REQUIRED);
                $("#nameError").html(t.NAME_IS_REQUIRED);
                $.scrollTo("#nameError");
                return false;
            }
            else {
                $("#nameError").html("");
            }

            var title = $.trim($("#mct").val());
            if(title.length > 30) {
                //app.helpers.window(t.SYSTEM_MESSAGE, t.NAME_CAN_BE_MAX_30_LETTERS_LONG);
                $("#nameError").html(t.NAME_CAN_BE_MAX_30_LETTERS_LONG);
                $.scrollTo("#nameError");
                return false;
            }
            else if ($("#mct").val() && title.length < 30) {
                $("#nameError").html("");
            }

            if(app.data.tags.length == 0) {
                //app.helpers.window(t.SYSTEM_MESSAGE, t.AT_LEAST_ONE_TAG_IS_REQUIRED);
                $("#tagsError").html(t.AT_LEAST_ONE_TAG_IS_REQUIRED);
                $.scrollTo("#tagsError");
                return false;
            }
            else {
                $("#tagsError").html("");
            }

            var duration = $.trim($("#id_duration").val());
            var isNumber = (duration - 0) == duration && duration.length > 0;
            if($("#id_duration").is(":visible") && (!isNumber || duration < 0 || duration > 999)) {
                //app.helpers.window(t.SYSTEM_MESSAGE, t.DURATION_MUST_CONSIST_OF_NUMBERS);
                $("#durationError").html(t.DURATION_MUST_CONSIST_OF_NUMBERS);
                $.scrollTo("#durationError");
                return false;
            }
            else {
                $("#durationError").html("");
            }

            if(app.data.owner!=$('#id_owner').val()) {
                app.helpers.window(t.SYSTEM_MESSAGE, t.CHANGE_OWNER_MSG, [{
                   'text': t.YES,
                    events: [{
                        name: 'click',
                        handler: function() {
                            sendContent(oldTags, newTags);
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

            } else if(app.data.owner==undefined || app.data.owner==$('#id_owner').val()) {
            	  fh.setContentCookie();
                sendContent(oldTags, newTags);
            }

        }
        return false;
    });
    


    function sendContent( oldTags, newTags) {
        for(var i = 0, len = app.data.tags.length; i < len; i++){
            if(app.data.tags[i].id != undefined){
                oldTags.push(app.data.tags[i].id);
            }else{
                newTags.push(app.data.tags[i].name);
            }
        }
        $.post("/content/manage/save/", JSON.stringify({
            "file_id": $("#id_file_id").val(),
            "title": $.trim($("#mct").val()),
            "expires_on": $("#datepicker").val() == t.DATE_NOT_SET ? '' : $("#datepicker").val(),
            "new_tags_names": newTags,
            "tags_ids": oldTags,
            "owner": parseInt($("#id_owner").val()),
            "selected_groups_ids": ContentManage.selectedGroupsIds(),
            "language": $("#id_language").val(),
            "duration": $.trim($("#id_duration").val()),
            "is_downloadable": $("#id_is_downloadable").is(":checked") ? 'checked' : '',
            "delete_after_expire": $("#id_delete_expired").is(":checked") ? 'checked' : '',
            "note": $("#id_note").val()
        }), function(data){
            if(data.status == "OK") {
                if($('#id_is_edited').val() == 'True'){
                    app.helpers.window(t.SYSTEM_MESSAGE, t.FILE_DETAILS_SAVED, null, null, function() {
                        window.location = "/content/manage";
                    });
                } else {
                    if (app.helpers.cookie.get('dont_show_popup_next_time') == "true") {
                        window.location = "/content/manage";
                    } else {
                        app.helpers.window(t.SYSTEM_MESSAGE, t.FILE_DETAILS_SAVED_ADDITIONAL + '<br /><br /><input type="checkbox" id="dont_show_popup_next_time" /> ' + t.DONT_SHOW_AGAIN, [
                            {
                                text: 'OK',
                                events: [
                                    {
                                        name: 'click',
                                        handler: function(e) {
                                            app.helpers.cookie.set('dont_show_popup_next_time', $('#dont_show_popup_next_time').is(':checked') ? 'true' : '');

                                            $.nmTop().close();
                                            window.location = "/content/manage";

                                            return false;
                                        }
                                    }
                                ]
                            }
                        ]);
                    }
                }
            }
        });
    }

    var onSuccessFileImport = function(data) {
        if (data.status == "OK") {
            $("#id_language").val(data.selected_language);
            $("#fileName").text(t.UPLOAD_COMPLETE + ': ' + data.file_orig_filename);
            $('#manageContentForm input[name="title"]').val(
                data.file_orig_filename
                    .substr(0, data.file_orig_filename.lastIndexOf('.')) || data.file_orig_filename
            );
            $("#id_file_id").val(data.file_id);
            $("#mcd").removeClass("button-disabled");
            $('#fileTypeIco').addClass('fileType' + data.file_type);

            if (data.is_duration_visible == "True") {
                $("li#duration").show();
            }
            app.data.changed = true;
        } else {
            $("#fileName").text(t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["message"]);
            $("#file").val("");
            app.helpers.window(t.SYSTEM_MESSAGE, t.UNSUPPORTED_FILE_TYPE);
            if ( $('#chooseFromDms').hasClass("previously-disabled") ) {
								$('#ufm').removeAttr('disabled');
								$('#ufm').removeClass('button-disabled');
						}
						else {
								$('#ufm, #chooseFromDms').removeAttr('disabled');
								$('#ufm, #chooseFromDms').removeClass('button-disabled');
						}
        }
    };

    $('#importFileForm').live('submit', function() {
        try {
						if ( $('#chooseFromDms').hasClass("button-disabled") ) {
								$('#chooseFromDms').addClass('previously-disabled');
						}
            $('#ufm, #chooseFromDms').attr('disabled', 'disabled');
            $('#ufm, #chooseFromDms').addClass('button-disabled');
            $("#fileName").text('Uploading: '+$("#file").val());
            $(this).ajaxSubmit({
                success: function(data) {
                    onSuccessFileImport(data);
                    clearTimeout(app.config.progress.t);
                    $('#progressWrapper').hide();
                    // $('#cancelUpload').hide();
                },
                dataType: 'json'
            });

        }catch(err) {}
        $('#progressWrapper').show();
        $('#cancelUpload').show();
        if(typeof app.config.progress != 'object'){
            app.config.progress = {};
        }
        app.config.progress.v = 0;
        app.config.progress.t = false;
        app.config.progress.t = setInterval(function(){
            $('#progress').css({
                'backgroundPosition': (++app.config.progress.v)+'px 0px'
            });
        }, 40);
        return false;
    });

    $('#cancelUpload').click(function() {
				$('#progressWrapper').hide();
				$('#cancelUpload').hide();
                $('#duration').hide();

				if ( $('#chooseFromDms').hasClass("previously-disabled") ) {
						$('#ufm').removeAttr('disabled');
						$('#ufm').removeClass('button-disabled');
				}
				else {
						$('#ufm, #chooseFromDms').removeAttr('disabled');
						$('#ufm, #chooseFromDms').removeClass('button-disabled');
				}
		$("#fileName").text("");
		$("#mcd").addClass("button-disabled");
		$('#fileTypeIco').removeClass('fileType10 fileType20 fileType30 fileType40 fileType50 fileType60 fileType70 fileType80 fileType90');
        $("#manageContentForm input[name='title']").val('');
		return false;
    })

    $('.filetree li span.file').live('click', function() {
				if ( $('#chooseFromDms').hasClass("previously-disabled") ) {
						$('#ufm').removeAttr('disabled');
						$('#ufm').removeClass('button-disabled');
				}
				else {
						$('#ufm, #chooseFromDms').removeAttr('disabled');
						$('#ufm, #chooseFromDms').removeClass('button-disabled');
				}

       $.post("/content/dms/", JSON.stringify({
                "file_path": $(this).parent().attr("id"),
                "file_name": $(this).text()
            }), function(data) {
                onSuccessFileImport($.parseJSON(data));
            });
       $.nmTop().close();
    });

    $('#sft').click(function(){
        app.helpers.window(t.SUPPORTED_FILE_TYPES, $("#sftHidden").html());
    });

    app.helpers.autocomplete('#newTag');

    $('#addTag').click(function(){
        app.callbacks.handleTags('#newTag');
        app.data.changed = true;
        $('#newTag').blur().focus();
        return false;
    });
    $('#newTag').keyup(function(event){
        app.callbacks.handleTags('#newTag', event);
				if (event.keyCode == '13') {
						$(this).blur().focus();
				}
    });
    $( "#datepicker" ).datepicker({
		showOn: "button",
		buttonImage: mediaURL + "img/blank.gif",
		buttonImageOnly: true,
        dateFormat: 'yy-mm-dd',
        minDate: +7
	}).change(function(){
	    if($(this).val() && $(this).val() != t.DATE_NOT_SET){
	        $('#id_delete_expired').removeAttr('disabled');
	    }else{
	        $('#id_delete_expired').attr('disabled', 'disabled').removeAttr('checked');
	    }
        app.data.changed = true;
	});
	if(!$( "#datepicker" ).val() || $( "#datepicker" ).val() == t.DATE_NOT_SET){
	     $('#id_delete_expired').attr('disabled', 'disabled')
	}
    $('#ufm').file().choose(function(e, input) {
        input.attr("style", "display: none;");
        input.attr("id", "file");
        input.attr("class", "file");
        input.attr("name", "file");
        $("#file").replaceWith(input);
        $(this).parents('form').submit();
    });

    // -- custom select boxes
    $('#languageWrapper select').addClass('selectBoxJs');
    $('#ownersWrapper select').addClass('selectBoxJs');
    $(".selectBoxJs").sb();

    // -- adding tags to internal data sotrage
    $('#tagList').children('li').each(function(){
       app.data.tags.push({id: $(this).attr('id').replace('tag_', ''), name: $.trim($(this).text())});
    });
    // -- applying default tag behavior to tags read from server-side
    var helper = new app.elements.tag('dummy tag');
    $('#tagList').children('li').click(function(){
        helper.events[0].handler.apply(this, arguments);
    });
    
	fh.init();

    //localScroll
		$.localScroll();

});
