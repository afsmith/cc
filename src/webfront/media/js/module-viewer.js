var app = new Ing();
var playingIndex = 0;
var playingId = null;
var singleModuleMode = false;
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    
    app.config.ocl_token = $('#ocl_token').text();
    if(moduleID){
      app.module.get(moduleID, 'json', true);
    }
    if (!singleModuleMode) app.module.addViewerEvents();
    
    var handleSMM = function() {
       $('#video').hide();
       $('#footer').addClass('smm-footer');
 	   $('#playLesson').show();
 	   $('#playLesson').click(function(){
 		   app.module.addViewerEvents();
    	   $('#playLesson').remove();
 		   $('#video').show();
     	   playM();
 	   });
 	   $(window).on('resize', function(){
 		   var winSize = {width: window.innerWidth,
 				   		  height: window.innerHeight},
 			   contentCord = {},
 			   contentSize = {};
 		   
 		   $('#topContentHolder').height(winSize.height * 0.1);
 		   $('#bottomContentHolder').height(winSize.height * 0.1);
 		   contentCord = $('.userView > .wrapper > .dbMiddle').offset();
 		   contentSize = {width: (winSize.width - $('.userView > .wrapper > .dbMiddle').innerWidth())/2,
 				   		  height: $('.userView > .wrapper > .dbMiddle').innerHeight()};
 		   $('#leftContentHolder').offset({top: contentCord.top});
 		   $('#leftContentHolder').width(contentSize.width);
 		   $('#leftContentHolder').height(contentSize.height);
 		   $('#rightContentHolder').offset({top: contentCord.top});
 		   $('#rightContentHolder').width(contentSize.width);
 		   $('#rightContentHolder').height(contentSize.height);
 	   });
 	   $(window).trigger('resize');
    }
    
    if(this.location.hash){
        if ( this.location.hash.indexOf("#/") > -1 ) {
            playingId = this.location.hash.replace(/#\//, '');
            if(moduleID){
                var url = '/content/modules/' + moduleID + '/?format=json';
                $.get(url, function(data) {
                    $.each(data.track0, function(i, v) {
                        if ( playingId == v.segment_id ) {
                            playingIndex = v.start;
                        }
                    });
                    if (singleModuleMode) { handleSMM(); } else playM();
                });
            }
        }
        else {
            playingIndex = this.location.hash.replace(/#/, '');
            if (singleModuleMode) { handleSMM(); } else playM();
        }
    }
    else {
       if (singleModuleMode) { handleSMM(); } else playM();
    }

    $('#courseObjective').click(function(){
        var elements = $("#moduleList").find('li').length;
        if ( app.data.activeItem < elements ) {
        	Ing.findInDOM().player.api.pause();
        }
        app.module.displayObjective(app.data.moduleJSON, true);
        return false;
    });

    $('#courseSignOff').click(function(){
          app.helpers.window(
               t.SYSTEM_MESSAGE,
               t.SIGN_OFF_MESSAGE+'<br/><br/>',
               [{
                   'text': t.CONFIRM,
                   events: [{
                       name: 'click',
                       handler: function(){
                           $.get($('#courseSignOff').attr('href'),
                                function(data, status, xmlHttpRequest){
                                    if(typeof data != 'object'){ // IE bug --
                                        data = $.parseJSON(data);
                                    }
                                    if(data.status == 'OK'){
                                        $('#courseSignOff').hide();
                                        $.nmTop().close();
                                        return false;
                                    }else{
                                        app.helpers.window(t.SYSTEM_MESSAGE,
                                            t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["error"]);
                                    }
                            });
                       }
                   }]
               },{
                   'text': t.CANCEL,
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

    $('.nyroModalClose').live('click', function() {
        document.getElementById('video').resume();
        app.triggerEvent('modalClosed');
    });
    $(app).bind('modalClosed', function(){
        //app.module.startPlayback(moduleID);
    });
	$('.shelf').each(function() {
			var container = $(this).parent();
			$(container).siblings(".prev, .next").addClass('disabled');
	});
	shelfEach();

    $('#loginForm input').keyup(function(event){
       if(event.keyCode == 13){
           $('#loginForm').submit();
       }       
    });   
});

function shelfEach() {
		if ( $('.shelf').width() == 0 ) {
				setTimeout ( "shelfEach()", 200 );
		}
		else {
				$('.shelf').each(function() {
						var elements = $(this).find('li').length;
						var container = $(this).parent();
						if (elements < 6) {
							$(container).siblings(".prev, .next").addClass('disabled');
						} else {
							$(container).siblings(".prev, .next").removeClass('disabled');
						}
				});
		}
}

function playM() {
    if(app.helpers.cookie.get('ing_obj_' + moduleID) != ''){
    	app.player.playEmbedded(moduleID, 'playlist', false, playingIndex);
        res = setTimeout("$(window).resize()", 100);
    }
}
