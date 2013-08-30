var app = new Ing();
var formTimer = false;
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.loadFiles();
    // -- event proxies
    $('#submitTags').click(function(){
        app.callbacks.handleTags('#id_tags_ids');
        $("#id_tags_ids").blur().focus();
        return false;
    });
    $('#id_tags_ids').focus(function(event){
        if($(this).val() == t.ADD_TAG){
            $(this).val('');
        }
    }).keyup(function(event){
				app.callbacks.handleTags('#id_tags_ids', event);
				if (event.keyCode == '13') {
						$(this).blur().focus();
				}
    });
    // -- roller item event
    $('.singleFile').live('click', function(){
        app.helpers.displayDetails(app.data.files[$(this).attr('id').substr(5)]);
        $('#rollerItems li').removeClass('active');
        $(this).parent().addClass('active');
        return false;
    });
    $('#rollerWrapper').on('loaded', function() {
    	var fileId = window.location.hash.replace(/#/, ''),
    		filesMap,
    		active= [],
    		naviDots;
    	if (!!fileId) {
    		filesMap = app.data.map;
    		$.each(filesMap, function(key, value) {
    			if (value.hasOwnProperty('id') && value.id == fileId) {
    				active.push(key);
    			}
    		});
    		if (!!!active[0]) return;
			$('#rollerItems').css('left', Math.abs($('#rollerItems').position().left) - $('#' + active[0]).parent().position().left);
			naviDots = $('.navi a');
			naviDots.toggleClass('active', false);
			$.each($('#rollerItems ul'), function(key, value){
				if (value.id == $('#' + active[0]).parent().attr('id')) {
					$(naviDots[key]).addClass('active');
				}
			});
			$('#' + active[0] + ' .singleFile').click();
    	}
		return;
    });
    app.helpers.autocomplete('#id_tags_ids');
    $('#search').submit(function(event){
      event.type = 'submit_search'; // -- patch for IE bug
      app.triggerEvent(event);
    });
    $(app.config.myFilesInput + ', ' + app.config.inactiveFilesInput + ', ' + app.config.fromMyGroups).change(function(event){
      submitSearch();
    });
    // -----------------------
    $('#rollerWrapper .prev').addClass('disabled');
    // -- custom select boxes
    $('#search select').addClass('selectBoxJs');
    $(".selectBoxJs").sb();
    $('#id_file_name').keyup(function(event){
				submitSearch();
    });
    $('#search select').change(function(event){
        submitSearch();
    });
    $('#tagList').droppable({
        activeClass: 'tagListActive',
        tolerance: 'touch',
        'drop': function(event, ui){
            app.callbacks.handleTags('#' + $(ui.draggable).attr('id'));
        }

    });
    $('#removeFile').live('click', function(e){
       e.preventDefault();
       var url = $(this).attr('href');
       app.helpers.window(
           t.SYSTEM_MESSAGE,
           t.FILE_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.post(
                         '/content/manage/' + url,
                         '',
                         function(data, status, xmlHttpRequest){
                              $('#fileDetails').html('');
                              app.helpers.window(t.SYSTEM_MESSAGE, t.FILE_REMOVED);
															submitSearch();
                              return false;
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

    // proper tagfield width
		app.helpers.taglist();

		searchDefault = $('#id_file_name').val();
    $('#id_file_name').focus(function() {
    	if(searchDefault == $('#id_file_name').val()) {
    		$('#id_file_name').val('');
    	}
    });
    $('#id_file_name').blur(function() {
    	if($('#id_file_name').val() == '') {
    		$('#id_file_name').val(searchDefault);
    	}
    });

    $('#refresh').click(function(){
        location.reload(true);
    });

});
var searchDefault;
function submitSearch(){
    clearTimeout(formTimer);
    formTimer = setTimeout("if ( $('#id_file_name').val() == searchDefault ) { $('#id_file_name').val(''); $('#search').submit(); $('#id_file_name').val(searchDefault); } else { $('#search').submit(); }", 1000);
}
