var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    
    $(".selectBoxJs").sb();
    $('#userLessons li.first').next().css('left', $('#userLessons li.first').width() - 14);
    $('.browse').click(function(){return false;});
	$('.tabs a').click(function(){
		$('div.result').hide();
		$('#userLessons li').removeClass('active');
		$(this).parent().addClass('active');
		$($(this).attr('href')).fadeIn('200');
		$('.rollerItems').each(function() {
			var width = $(this).width();
			var container = $(this).parent();
			var container_width = $(container).width();
			if (width < container_width) {
				$(container).siblings(".prev, .next").find('.browse').hide();
			} else {
				$(container).siblings(".prev, .next").find('.browse').show();
			}
		});
		return false;
  	});
  	$('#user_groups').change(function(){
  		$('.singleLessonWrapper').hide();
  		if($(this).val() != 0){
	  		$('.' + $(this).val()).show();
	  	}else{
	  		$('.singleLessonWrapper').show();
	  	}
  	});
  	$('.rollerItems ul').css('width', function(){
  		return $(this).children('li').length * ($(this).children('li:first').width() + 24);
  	});
  	app.config.shelfWrapperWidth = 591;
  	var t = app.config.other.timer;
  	var moved = false;
  	$('.next, .prev').mousedown(function(){
  		var dir = $(this).hasClass('next') ? 'right' : 'left';
  		var id = '#' + $(this).siblings('.roller').children('div').attr('id');
//  		console.log('#' + $(this).siblings('.roller').children('div').attr('id'));
  		t = setInterval(function(){
	  			app.helpers.move(dir, app.config.other.movingStep, id);
	  			moved = true;
  			}, app.config.other.movingInterval);
  	}).mouseup(function(){
  		if (!moved){
  	  		var dir = $(this).hasClass('next') ? 'right' : 'left';
  	  		var id = '#' + $(this).siblings('.roller').children('div').attr('id');
  			app.helpers.move(dir, 60, id);
  		}
  		if(t){
  			clearTimeout(t);
  			moved = false;
  		}
  	});

    $("#sendMessageToLessonOwner").live('click', function() {
        var ownerid = $(this).attr("ownerid");
        var ownername = $(this).attr("ownername");
        var course_id = $(this).attr("course_id");
        if(ownerid != "" && ownername != "") {
            app.callbacks.openCompose(ownername, [ownerid], $(this).next().text(), course_id);
        } else {
            app.helpers.window(t.SYSTEM_MESSAGE, t.MODULE_NO_OWNER);
        }
    });

    $('#myFinishedLessons').hide();
    $('.singleFile, .lessonDetails .title a, .courseApla, .playLesson, #sendMessageToLessonOwner').tooltip({
    	position: "bottom center",
    	// effect: 'slide',
    	predelay: 500,
    	onBeforeShow: function(tooltip, position) {
    		$("body").append(this.getTip());
    	},
    	onHide: function(tooltip) {
    		$('body').children('.tooltip').remove();
    	},
    	offset: [10, 0]
    });
	$('.rollerItems').each(function() {
		var width = $(this).width(),
			container = $(this).parent(),
			container_width = $(container).width();
		
		if (width < container_width) {
			$(container).siblings(".prev, .next").find('.browse').hide();
		}
	});
});
