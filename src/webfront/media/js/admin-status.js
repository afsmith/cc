var ing = new Ing();
$(document).ready(function() {
    app.config.mediaURL = mediaURL;
    app.run();
    $.ajaxSetup({
    	error : function(x) {
    		$("body").html(x.responseText);
    	}
	});
    
    $('.widget').each(function() {
        var w = new window["app"]["widgets"][$(this).attr('id')]($(this).attr('id'));
        w.init();
    });
//	if(app.helpers.cookie.get('ing_admin_lastGroup') != 'null'){
//        $('#groupFilter').val(app.helpers.cookie.get('ing_admin_lastGroup'));
//    }
	
	var searchDefault = $('#groupFilter').val();
    $('#moduleFilter').live('focus', function() {
    	if(searchDefault == $('#moduleFilter').val()) {
    		$('#moduleFilter').val('');
    	}
    });
    $('#moduleFilter').live('blur', function() {
    	if($('#moduleFilter').val() == '') {
    		$('#moduleFilter').val(searchDefault);
    	}
    });
    
    $('#groupFilter').focus(function() {
    	if(searchDefault == $('#groupFilter').val()) {
    		$('#groupFilter').val('');
    	}
    });
    $('#groupFilter').blur(function() {
    	if($('#groupFilter').val() == '') {
    		$('#groupFilter').val(searchDefault);
    	}
    });
    
    var sortCourses = function(){
        $.each($('#completionDetails table.result'), function(){
	        var sortMap = [],
	        	currentTab = this,
	        	sources = $(currentTab).find('tr.resultRow'),
	        	values = sources.find('.titleColumn');
	        
	        $(currentTab).find('tr.first').removeClass('first');
	        $(currentTab).find('tr.last').removeClass('last');
	        for (var i = 0, srcLen = sources.length; i < srcLen; i++ ){
	        	sortMap.push([sources[i], $(values[i]).text().toLowerCase()])
	        }

	        sortMap.sort(function(a,b){
	             if(a[1] > b[1]){
	                return 1;
	             }
	             if(a[1] < b[1]){
	                return -1;
	             }
	             return 0;
	        });
	        
	        $(currentTab).empty();
	        $.each(sortMap, function(index, value){
	        	if (index%2) {
	        		$(value[0]).toggleClass('even', true);
	        		$(value[0]).toggleClass('odd', false);
	        	} else {
	        		$(value[0]).toggleClass('even', false);
	        		$(value[0]).toggleClass('odd', true);
	        	}
	        	if (index == 0) { $(value[0]).toggleClass('first', true); }
	        	if (index == sortMap.length - 1) { $(value[0]).toggleClass('last', true); }
	            $(currentTab).append(value[0]);
	        });
        });
    }
    sortCourses();
    
    $('#sendMessageToGroup').live('click', function(){
        if(!($(this).hasClass('button-disabled'))){
          ing.callbacks.openCompose($('#groupsList .active').find('.groupName').text(), getIdsFromSelectedGroup());
        }
        return false;
    });
    
    $('#showMy').change(function() {
        var tmp = $('#allGroupsList').html();
        $('#groupsList').find('li').show();
        $('#groupsList').find('li.active').removeClass('active');
    	$('#groupDetailsWrapper').toggleClass('hidden', true);
    	$('#defaultLabel').toggleClass('hidden', false);
        $('#allGroupsList').html($('#groupsList').html());
        $('#groupsList').html(tmp);
        $("#groupFilter").val(searchDefault);
        $("#moduleFilter").val(searchDefault);
    });
    
    $('#groupsList li').live('click', function(event){
    	$('#defaultLabel').toggleClass('hidden', true);
    	$('#groupDetailsWrapper').toggleClass('hidden', false);
    	if (!$(this).hasClass('active')) {
	    	$('#groupsList li.active').toggleClass('active', false);
	    	$(this).toggleClass('active', true);
            $.get('assignments/group_status/'+ $(this).attr('value'),
                  [],
                  function(data) {
                    $('#groupDetailsWrapper').html(data);
                    console.log(data);
            });
	    //	$('#completionDetails').children('table:not(.hidden)').toggleClass('hidden', true);
	    //	$('#completionDetails').children('table[value=' + $(this).attr('value') + ']').toggleClass('hidden', false);
	    	$('#moduleFilter').trigger('keyup');
    	}
    });

	$('#groupFilter').keyup(function(){
		$('#groupsList .groupName').each(function(){
			if($(this).text().toLowerCase().indexOf($.trim($('#groupFilter').val().toLowerCase())) == -1){
				$(this).parent().hide();
			}else{
				$(this).parent().show();
			}
		});
	});
	$('#moduleFilter').live('keyup', function(){
		$('#completionDetails table:not(.hidden)').find('.titleColumn').each(function(){
			if($(this).text().toLowerCase().indexOf($.trim($('#moduleFilter').val().toLowerCase())) == -1 
				&& $('#moduleFilter').val() != searchDefault){
				$(this).parent().hide();
			}else{
				$(this).parent().show();
			}
		});
	});
//	$('#completionDetails .completionColumn a[class*=progress]').tooltip({predelay: 500});

    var getIdsFromSelectedGroup = function() {
        return $.parseJSON($('#groupsList .active').attr('type'));
    }

    var getSelectedIds = function() {
        var ids = [];
        var group = $("#groupFilter").val();
        $("#adminStatus").find('#rdw_'+ group +' :checked').each(function() {
            ids.push(jQuery(this).attr("id").split("_")[2]);
        });
        return ids;
    };

    var getSelectedNames = function() {
        var names = [];
        var group = $("#groupFilter").val();
        $("#adminStatus").find('#rdw_'+ group +' :checked').each(function() {
            names.push(jQuery(this).next().text());
        });
        return names;
    };

    $("#sendMessageToUsers").live('click', function() {
        var selectedIds = getSelectedIds();
        if(selectedIds.length > 0) {
            ing.callbacks.openCompose(getSelectedNames(), selectedIds);
        }
    });
});
