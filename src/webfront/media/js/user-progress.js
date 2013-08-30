var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.player.trackUser = false;
  	app.config.shelfWrapperWidth = 492;
  	var timer = app.config.other.timer;
    $.ajax({
        url: '/content/modules/' + moduleID + '/?format=json',
        success: function(data){
            if(typeof data != 'object'){ // IE bug --
                data = $.parseJSON(data);
            }
            app.data.module = data;
            app.data.segments = {};
            app.data.activeSegment = false;
            for(var i = 0, len = data.track0.length; i < len; i++){
                app.data.segments[data.track0[i].segment_id] = data.track0[i];
                if(data.track0[i].start == 0){
                    app.data.activeSegment = data.track0[i];
                }
            }

            //if ($('results_tracking_'+app.data.activeSegment.segment_id).children().length > 0)
            //	$('#scormResults').show();

    }, async: false});
    
	var searchDefault = $('#userFilter').val();
    $('#userFilter').focus(function() {
    	if(searchDefault == $('#userFilter').val()) {
    		$('#userFilter').val('');
    	}
    });
    $('#userFilter').blur(function() {
    	if($('#userFilter').val() == '') {
    		$('#userFilter').val(searchDefault);
    	}
    });
	$('#userFilter').keyup(function(){
		$('#usersList .userName').each(function(){
			if($(this).text().toLowerCase().indexOf($.trim($('#userFilter').val().toLowerCase())) == -1){
				$(this).closest('li').hide();
			}else{
				$(this).closest('li').show();
			}
		});
	});
    
    $('#usersList li').live('click', function(event){
    	var clickedDetails = $(this).attr('value');
    	$('#defaultLabel').toggleClass('hidden', true);
    	$('#moduleProgressWrapper').toggleClass('hidden', false);
    	if (!$(this).hasClass('active')) {
	    	$('#usersList li.active').toggleClass('active', false);
	    	$(this).toggleClass('active', true);
	    	app.helpers.throbber('#moduleProgressWrapper');
	    	$.get(
	    		'/assignments/user/progress/?user_id=' + clickedDetails + '&course_id=' + moduleID, 
	    		function(data){
	    			$('#moduleProgressWrapper').html(data);
	                app.helpers.throbber('#moduleProgressWrapper', 'remove');
	                
	            	$('#userLog .result:first, .segmentDetails:first').show();
	            	$('.rollerItems li:first').addClass('active');
	            	
	            	if ( $('.progress_tracking') ) {
	        			$('.progress_tracking').each(function(index) {
	        					app.data.activeTracking = $(this).attr('id');
	        					var results_tracking_id = '#'+app.data.activeTracking.replace('progress_', 'results_');
	        					if($(results_tracking_id).children().length > 0) {
	        							$(this).css('cursor','pointer');
	        					}
	        			});
	            	}
	                
	            	$('.rollerItems ul').css('width', function(){
	              		return $(this).children('li').length * ($(this).children('li:first').width() + 24);
	              	});
	                
	                $('.rollerItems').each(function() {
	            		var width = $(this).width();
	            		var container = $(this).parent();
	            		var container_width = $(container).width();
	            		
	            		if (width < container_width) {
	            			$(container).siblings(".prev, .next").addClass('disabled');
	            		} else {
	            			$(container).siblings(".prev, .next").removeClass('disabled');
	            		}
	                });
	                $('.prev a').hide();
	    		});
    	}
    });
    
    var updateMsgLabel = function(){
    	var selectedUsers = $('#usersList').find('.userSelect:checked').length;
    	$('#sendMessageToUsers').find('label').text(t.SEND_TO_PEOPLE.replace('{0}', selectedUsers));
    };

    var getSelectedIds = function() {
    	var ids = [],
    		checked = $('#usersList').find('.userSelect:checked');
    	$.each(checked, function(index){
    		ids.push(checked[index].name);
    	});
        return ids;
    };

    var getSelectedNames = function() {
        var names = [];
        $("#usersList .userSelect:checked").parent().each(function() {
            names.push($(this).text());
        });
        return names;
    };
    
    $('#usersList li:visible .completion div[class*=progress]').tooltip({ predelay: 500});

    $("#sendMessageToUsers").live('click', function() {
        var selectedIds = getSelectedIds();
        if(selectedIds.length > 0) {
            app.callbacks.openCompose(getSelectedNames(), selectedIds);
        }
    });
    
    $('#selectAll').on('change', function(){
    	$.each($('#usersList').find('.userSelect'), function(){
    		$(this).attr('checked', $('#selectAll').is(':checked'));
    	});
    	updateMsgLabel();
    });
    
    $('#usersList').find('.userSelect').on('change', function(){
    	updateMsgLabel();
    });
    
	$('.segmentDetails .singleFile').click(function(){return false;});
	$('.rollerItems .singleFile').live('click', function(){
	    app.data.activeSegment = app.data.segments[$(this).attr('id').replace('segment_', '')];
		var id = $(this).attr('id');
		$('.rollerItems li').removeClass('active');
		$(this).parent().addClass('active');
		$('#userLog .result, .segmentDetails').hide();
		$('#details_'+id + ', #progress_'+id).show();
		$('#scormResults .result, .segmentDetails').hide();
		$('#details_'+id + ', #results_'+id.replace('segment_','tracking_')).show();
		if ($('#results_tracking_'+id).children().length == 0)
			$('#scormResults').hide();
		else
			$('#scormResults').show();
		return false;
	});
	
    $('.hasCard input[type=checkbox]').live('click', function() {
        var input = this;
        var enable = this.checked;
        var userId = $(this).attr('id').split('_')[3];
        $.post('/management/users/' + userId + '/has_card/',
               JSON.stringify({'has_card': enable}),
               function(data, status, xmlHttpRequest) {
                   if (data.status == 'OK') {
                       input.checked = enable;
                   } else {
                       // console.log(JSON.stringify(data));
                   }
               });
        return false;
    });

    $('.progress_tracking').click(function(){
        $('#scormResults').hide();
        $('#scormResults ul').hide();
        app.data.activeTracking = $(this).attr('id');
        var results_tracking_id = '#'+app.data.activeTracking.replace('progress_', 'results_');
        if($(results_tracking_id).children().length > 0) {
            $(results_tracking_id).show();
            $('#scormResults').show();
        }
    });
    $('.page_tracking_link').live('click', function(){
        var end_event_id = $(this).children('li').attr('id').split('_')[2];
        $.nmManual('/tracking/user_page_progress/'+end_event_id);
    });
	$('#mainScroller.rollerItems .courseApla').live('click', function() { $(this).prev().click(); });
  	$('.next, .prev').live('mousedown', function(){
  		var dir = $(this).hasClass('next') ? 'right' : 'left';
  		var id = '#' + $(this).siblings('.roller').children('div').attr('id');
  		timer = setInterval(function(){
	  			app.helpers.move(dir, app.config.other.movingStep, id);
  			}, app.config.other.movingInterval);
  	}).live('mouseup', function(){
  		if(timer){
  			clearTimeout(timer);
  		}
  	});
  	$('.preview').live('click', function(event){
        event.preventDefault();
        var obj = app.data.activeSegment,
            href = $(this).attr('href'),
            wraperId = (app.config.player.mode == "html5")? 'video': 'mplayer',
            playerObj = $('<div class="mplayerWrapper"><a href="javascript:void(0);" class="closeFW"></a><div id="' + wraperId + '"></div></div>');
        
        app.player.playModal(obj, playerObj, "opaque");
    	if (app.config.player.mode == 'html5') {
    		// app.player.appendControls(document.getElementById('video'));
    		app.player.adjustControls();
        	if (app.data.filetypes[obj.type] != "video" 
        		&& app.data.filetypes[obj.type] != "music") $('#mediaControls').toggleClass('disabled', true);
        	if (app.data.filetypes[obj.type] != "image") $('#imageControls').toggleClass('disabled', true);
        	$('#video').on('mousemove', app.player.handleMousemove);
        	$(app.player.domInstance).on(app.player.api.mediaEvents.join(' '), app.player.mediaEventsHandler);
    	}
        return false;
    });
    $(app).bind('shelfStart', function(event, data){
         $('.prev a').hide();
         $('.next a').show();
    });
    $(app).bind('shelfStop', function(event, data){
         $('.next a').hide();
         $('.prev a').show();
    });
    $(app).bind('shelfMoving', function(event, data){
         $('.next a, .prev a').show();
    });
});
