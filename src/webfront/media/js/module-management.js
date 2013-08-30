var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.data.dirtyForm = false;
    app.run();
    $('#moduleMD_wrapper, #modulePD_wrapper, #moduleDD_wrapper').hide();
    $('#moduleMD, #modulePD, #moduleDD').hide();    //
    $('.operationBtn').hide();
    $("#mngMyModulesDetailsWrapper").hide();
    app.mm.loadModules(this.location.hash.replace(/#/, ''));
    app.config.searchForm = false;
    $("#id_owner").sb();

    var checkFormMsg = t.MODULE_MODIFIED;
    var saveFormAction = app.mm.saveModule;
    var validateModule = function() {
        if (!$("#moduleTitle").val()) {
            app.helpers.window(t.SYSTEM_MESSAGE, t.TITLE_IS_REQUIRED);
            return false;
        }

        if ($("#moduleTitle").val().length  > 30) {
            app.helpers.window(t.SYSTEM_MESSAGE, t.TITLE_CAN_BE_MAX_30_LETTERS_LONG);
            return false;
        }

        return true;
    }

    $('#mngMyModulesDetailsWrapper input[type=text],textarea,.delete,#allow_download,#allow_skipping,#id_language').change(function() {
        app.data.dirtyForm = true;
    });


    $(app).bind('tagRemoved', function(){
        app.data.dirtyForm = true;
    });

    $(".selectBoxJs, #moduleLanguageWrapper select").sb();
    $( "#moduleDate" ).datepicker({
        showOn: "button",
        buttonImage: mediaURL + "img/blank.gif",
        buttonImageOnly: true,
        dateFormat: 'yy-mm-dd',
        minDate: +7
    });

    $('.myModules li').live('click', function(){
        var elem = $(this);
        var ing = Ing.findInDOM();
       	app.helpers.checkForm(checkFormMsg, saveFormAction, function(){
            $('.myModules li').removeClass('active');
            elem.addClass('active');
            app.mm.setActiveModule(elem);
            app.mm.displayModuleDetails(elem);
            $('.operationBtn').hide();
            $(eval(app.data.map[elem.attr('id')].available_actions)).each(function(){
               $('#button-'+this).show().removeClass('inactive').addClass(this[1] || '');
            });
            if(app.data.activeModule.state_code == 1){
                $('#editModule').removeClass('inactive');
            }else{
                $('#editModule').addClass('inactive');
            }
            // -- piece of crapy code, I know...
            if(app.data.activeModule.state_code == 2 ||
                app.data.activeModule.state_code == 3 ||
                app.data.activeModule.state_code == 4){
                $('#moduleAssignments').show();
            }else{
                $('#moduleAssignments').hide();
            }

						var ing = Ing.findInDOM();
            window.location.hash = ing.data.activeModule.id;
        }, validateModule);

        var ing = Ing.findInDOM();
        window.location.hash = ing.data.activeModule.id;
     });
    $('#cloneModule').click(function(e){
        e.preventDefault();
       if(app.data.activeModule){
           app.helpers.checkForm(checkFormMsg, saveFormAction, function(){document.location.href = '/content/copy/' +  app.data.activeModule.id + '/'}, validateModule);
       }else {
           app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_MOD_COPY);
       }
       return false;
    });
    $('#createModule').click(function(e){
        e.preventDefault();
        var button = this;
        // alert(app.data.activeModule);
        if(app.data.activeModule){
            app.helpers.checkForm(checkFormMsg, saveFormAction, function(){document.location.href = $(button).attr('href')}, validateModule);
        } else {
        	window.location = $(button).attr('href');
            return true;
        }
        return false;
    });
    var closemm = $('#moduleManage').siblings('.close');
    if ($(closemm).length > 0) {
	    $(closemm).click(function(e){
	        e.preventDefault();
	        var button = this;
	        // alert(app.data.activeModule);
	        if(app.data.activeModule){
	            app.helpers.checkForm(checkFormMsg, saveFormAction, function(){document.location.href = $(button).attr('href')}, validateModule);
	        } else {
	        	window.location = $(button).attr('href');
	            return true;
	        }
	        return false;
		});
    }

    $('#editModule').click(function(e){
       if($(this).hasClass('inactive')){
           return false;
       }
       e.preventDefault();
       if(app.data.activeModule){
           app.helpers.checkForm(checkFormMsg, saveFormAction, function(){document.location.href = '/content/create/' +  app.data.activeModule.id + '/'}, validateModule);
       }else{
           app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_MOD_EDIT);
       }
       return false;
    });
    $('#moduleAssignments').click(function(e){
       e.preventDefault();
       if(app.data.activeModule){
           app.helpers.checkForm(checkFormMsg, saveFormAction, function(){document.location.href = '/content/modules/assign/#' +  app.data.activeModule.id}, validateModule);
       }else{
           app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_MOD_EDIT);
       }
       return false;
    });
    $('#search').keyup(function(){
        $('.moduleName').each(function(){
            if($(this).html().toLowerCase().indexOf($.trim($('#search').val().toLowerCase())) == -1){
                $(this).parent('li').hide();
            }else{
                $(this).parents('li').show();
            }
        });
    });

    $('#id_owner').change(function() {
        $('.moduleName').each(function() {
            if ($('#id_owner').val() && $('#id_owner').val() != $(this).attr('ownerid')) {
                $(this).parent('li').hide();
            } else {
                $(this).parents('li').show();
            }
        });
    });

    $('#moduleTitle, #moduleObjective, #moduleLanguageWrapper select, #moduleDate').change(function(){
        app.data.dirtyForm = true;
    });
    $('#addGroup').click(function(e){
        e.preventDefault();
        if($('#groupList').val() != -1){
            app.callbacks.handleTags('#groupList');
            app.data.dirtyForm = true;
        }
        //$('#groupList').sb('refresh');
        return false;
    });

    $('#moduleSave').click(function(e){
        e.preventDefault();
        if(!validateModule()) {
            return false;
        }
        	
        if(app.data.activeModule){
            app.mm.saveModule();
            app.data.dirtyForm = false;
        }else{
           app.helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_MOD_SAVE);
        }
        return false;
    });
    app.data.groups = {};
    $('#groupList option, #myGroupList option').each(function(){
        app.data.groups[$(this).html()] = $(this).attr('value');
    });

    $('.preview').live('click', function(){
        if(app.data.activeModule){
            var appConfig = app.config,
            	bg = $('<div class="modalBg"></div>'),
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
	        		'contentURL': '/content/modules/' + app.data.activeModule.id + '/?format=json',
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
	        	playerParams.contentURL = '/content/modules/' + app.data.activeModule.id + '/?format=xml',
	        	app.player.spawnFlash('video', appConfig.player.modalSize, playerParams, 'opaque');        	
	        }
        }
    });
    $('#button-activate, #button-reactivate, #button-back_to_draft').click(function(){
    	var button = this;
    	app.helpers.checkForm(checkFormMsg, saveFormAction, function(){
            $.post(
                "/content/modules/" + app.data.activeModule.id + "/state/",
                JSON.stringify({"new_state": $(button).attr("id").split("-")[1]}),
                function(data) {
                    if(data.status == "OK") {
                        app.mm.loadModules(app.data.activeModule.id);
                    } else {
                        //alert(data.messages);
												app.helpers.window(t.SYSTEM_MESSAGE, data.messages);
                    }
            });
           return false;
        })
    });

    $('#button-delete, #button-remove, #button-deactivate').live('click', function(e){
       e.preventDefault();
       var action = $(this).attr("id").split("-")[1];
       var message;
       if (action == 'delete' || action == 'remove')
       	message =  t.MODULE_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE;
       else
       	message = t.MODULE_DEACTIVATE_CONFIRM;
       var url = $(this).attr('href');
       app.helpers.window(
           t.SYSTEM_MESSAGE,
           message + '<br/>',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.post(
				            "/content/modules/" + app.data.activeModule.id + "/state/",
				            JSON.stringify({"new_state": action }),
				            function(data) {
				                if(data.status == "OK") {
				                    window.location.hash = "";
				                    $("#mngMyModulesDetailsWrapper").hide();
				                    app.mm.loadModules(app.data.activeModule.id);
				                } else {
				                    //alert(data.messages);
														app.helpers.window(t.SYSTEM_MESSAGE, data.messages);
				                }
				        });
				        $.nmTop().close();
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


    //$('#moduleMD_wrapper, #modulePD_wrapper, #moduleDD_wrapper').hide();
    //$('#moduleMD, #modulePD, #moduleDD').hide();    //
    //$('.operationBtn').hide();

    $('#button-activate, #button-remove, #editModule').show().addClass('inactive');

    $('#showMy').live('change', function() {
        var tmp = $('#groupList').html();
        $('#groupList').html($('#myGroupList').html());
        $('#myGroupList').html(tmp);
        $("#groupList").sb('refresh');
        $('#groupList').change();
    });

    $('#showMy').attr('checked', true);

    var searchDefault = $('#search').val();
    $('#search').focus(function() {
    	if(searchDefault == $('#search').val()) {
    		$('#search').val('');
    	}
    });
    $('#search').blur(function() {
    	if($('#search').val() == '') {
    		$('#search').val(searchDefault);
    	}
    });

		//$('textarea[maxlength]').limitMaxlength();

		$('textarea[maxlength]').keyup(function(){
				var max = parseInt($(this).attr("maxlength"));
				if($(this).val().length > max){
					$(this).val($(this).val().substr(0, $(this).attr('maxlength')));
				}
				//$(this).parent().find('.charsRemaining').html('You have ' + (max - $(this).val().length) + ' characters remaining');
			});

});
