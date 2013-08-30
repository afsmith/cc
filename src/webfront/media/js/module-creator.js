var app = new Ing();
var tim = [];
// formtimer - only in prototype
var formTimer = false;
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    app.loadFiles();
    if(moduleID){
      app.module.get(moduleID);
    }
    $(app).bind('shelfsLoaded', function() {
        //console.log('Dziala');
        addSortable();
        addDraggable();
    });
    if(app.helpers.cookie.get('ing_admin_lastShelf') != 'null'){
        app.shelf.loadShelfs(app.helpers.cookie.get('ing_admin_lastShelf'));
    }else{
        app.shelf.loadShelfs();
    }
    app.helpers.computeWidth('shelf');
    app.helpers.computeWidth('module');
    // -- event proxies
    $('#submitTags').click(function(){
        app.callbacks.handleTags('#id_tags_ids');
        $("#id_tags_ids").blur().focus();
        return false;
    });
    $('#id_tags_ids').focus(function(event){
        if($(this).val() == '- add tag -'){
            $(this).val('');
        }
    }).keyup(function(event){
        app.callbacks.handleTags('#id_tags_ids', event);
        if (event.keyCode == '13') {
						$(this).blur().focus();
				}
    });
    app.helpers.autocomplete('#id_tags_ids');
    $('#search').submit(function(event){
      event.type = 'submit_search'; // -- patch for IE bug
      app.triggerEvent(event);
    });
    $(app.config.myFilesInput + ", " + app.config.fromMyGroups).change(function(event){
      submitSearch();
    });

    // -----------------------

    $('#shelf ul, #module ul').css({
      'min-width': 762
    });
    $('#rollerWrapper .prev').addClass('disabled');

    var timer = false;
    var movingStep = 20;
    var shelfWidth = 0;
    var moduleWidth = 0;
    var elementToPosition = false;
    var allowRemoval = false;
    var files = [];
    var maxPage = 0;
    var nextURL = '/content/files/';
    var prevURL = false;
    var elementToDrop = {};

	// shelf and module
	function addSortable() {
			//console.log('addSortable function');
			$('#shelf ul, #module ul').sortable({ // allow to sort elements on shelf
					placeholder: 'holds',
					revert: false,
					tolerance: 'pointer',
					helper: function(event){
					        var clone = $(event.target).parents('li');
							return $('<div class="helper"></div>').attr('id', $(this).attr('id')).html( clone.html() );
					},
					start: function(){
						$('.overlay').remove();
					},
					stop: function(event, ui){
						//app.triggerEvent('itemChanged', [$(this).parents('.shelf').attr('id')]);
					},
					receive: function(event, ui){
						$(event.target).children('li').each(function(i) {
							if (!!!$(this).attr('id')) {
								$(this).attr('id', ui.helper[0].id);
							}
						});
						app.helpers.computeWidth('shelf');
						app.helpers.computeWidth('module');
						if($(this).parents('.shelf').attr('id') == $(ui.sender).parents('.shelf').attr('id')){
							allowRemoval = true;
						}else{
							allowRemoval = false;
						}
						addDraggable();
						if ( !allowRemoval ) {
		                app.triggerEvent('itemChanged', [$(this).parents('.shelf').attr('id')]);
		              }
					},
					appendTo: 'body',
					scroll: false,
					connectWith: '.ui-sortable'
			}).disableSelection();
	}

    // -- shelf and module
    function addDraggable(){
      $('#shelf ul li:not(.done), #module ul li:not(.done)').draggable({
          helper: function(event, element){
              var clone = $(event.target).parents('li').removeClass('done');
              return $('<div class="helper"></div>').attr('id', $(this).attr('id')).html( clone.html() );
          },
          appendTo: 'body',
          scroll: false,
          connectToSortable: '#shelf ul, #module ul',
          start: function(event, ui){
              $('.overlay').remove();
          },
          stop: function(event, ui){
              if(allowRemoval){
                $(event.target).remove();
                allowRemoval = false;
                app.triggerEvent('itemChanged', [$(this).parents('.shelf').attr('id')]);
              }

          }
      }).disableSelection().addClass('done');
    }
    // -- sound events
    $('.sound').droppable({
      tolerance: 'pointer',
      accept: function(element){
    	  return !!$(element).find('.fileTypeAudio').length;
//    	  return !!$(element).attr('id') && app.data.map[$(element).attr('id')].type == 30;
      },
      drop: function(event, ui){
        var tmp = $('<div class="active"><a href="#">' + $(ui.draggable).children('a').html() + '</a></div>');
        ui.draggable[0].id = ui.helper[0].id;
        tmp.children('a').children('img').remove();
        tmp.children('a').attr('title', tmp.children('a').html())
                         .html('snd')
                         .append(' <a href="#" class="remove_snd">(remove)</a>' +
                         '<a class="sndMode no-repeat" href="#"></a>');
        tmp.css('width', Math.max($(ui.draggable).width(), 139));
        tmp.attr('id', $(ui.draggable).attr('id'));
        elementToPosition = tmp;
        app.addInterfaces(tmp);
        elementToDrop = {obj: tmp, ttl: new Date()};
        //$(this).append(tmp);
        $(ui.draggable).remove();
      }
    }).bind('mouseout', function(event){
      elementToDrop = {};
    });
    // -- sound events
    $('.sound').mouseover(function(event){
        var mark = elementToDrop.ttl || false;
      if(elementToDrop.ttl && ((new Date()).getTime() - elementToDrop.ttl.getTime() < 2500)){
        elementToDrop.obj.css('position', 'absolute');
        $('.sound').append(elementToDrop.obj);
        elementToDrop = {};
      }
      snapToGrid(event.layerX || event.offsetX);
      if(mark){
        app.triggerEvent('itemChanged', [$(this).attr('id')]);
      }
    });
    $('.repeat').live('click', function(){
       $(this).removeClass('repeat').addClass('no-repeat');
       app.triggerEvent('itemChanged', ['sound']);
       return false;
    });
    $('.no-repeat').live('click', function(){
       $(this).removeClass('no-repeat').addClass('repeat');
       app.triggerEvent('itemChanged', ['sound']);
       return false;
    });
    // -- module event
    function snapToGrid(x){
      if(elementToPosition){
        var ints = parseInt(x / 139);
        var pos = x % 139;
        if(pos <= 139 / 2 && ints > 0){
          ints--;
        }
        elementToPosition.css('left', (ints * 139) + 'px');
        elementToPosition.css('top', '0px');
        elementToPosition = false;
      }
    }
    // -- creating overlays
    $('#shelf li img, #module li img').live('mouseover', function(){
      var overlay = $('<div class="overlay"><a class="close_overlay" title="' + t.ITEM_REMOVE + '"></a></div>');
      overlay.css({
        'left': $(this).parents('li').position().left + parseInt($(this).parents('li').css('margin-left')),
        'top': $(this).parents('li').position().top,
        'width': $(this).parents('li').outerWidth(),
        'height': $(this).parents('li').outerHeight()
      });
      overlay.appendTo($(this).parents('li'));
    });
    $('#shelf li img, #module li img').live('mouseout', function(){
      var that = this;
      tim[$(this).parent().parent().attr('id')] = setTimeout(function(){
            $(that).parent().removeClass('hover');
            $(that).parent().siblings('.overlay').remove();
      }, 50);
    });
    // -- overlay event
    $('.overlay').live('mouseover', function(){
      clearTimeout(tim[$(this).parent().attr('id')]);
      $(this).siblings('a').addClass('hover');
    });
    // -- overlay event
    $('.overlay').live('mouseout', function(){
        var that = this;
        tim[$(this).parent().attr('id')] = setTimeout(function(){
            $(that).siblings('a').removeClass('hover');
            $(that).remove();
        }, 5);
    });
    // -- overlay event
    $('.close_overlay').live('mouseover', function(){
        clearTimeout(tim[$(this).parent().parent().attr('id')]);
        var that = this;
        tim[$(this).parent().parent().attr('id')] = setTimeout(function(){
            $(that).parent('.overlay').siblings('a').removeClass('hover');
            $(that).parent('.overlay').remove();
        }, 5);
    });
    $('.close_overlay').live('mouseout', function(){
        clearTimeout(tim[$(this).parent().parent().attr('id')]);
    });
    $('.close_overlay').live('click', function(){
      var id = $(this).parents('.shelf').attr('id');
      $(this).parents('li').remove();
      app.helpers.computeWidth(id);
      if(id == 'module'){
        if(parseInt($('#module').css('left')) < -shelfWidth + $('#moduleWrapper').width() + 139){;
          app.helpers.move('right', movingStep, '#module');
          /*if(shelfWidth < $('#moduleWrapper').width()){
            $('#module').css({'left': 0});
          }*/
        }
      }else{
        if(parseInt($('#shelf').css('left')) < -shelfWidth + $('#shelfWrapper').width() + 139){
          app.helpers.move('right', movingStep, '#shelf');
          if(shelfWidth < $('#shelfWrapper').width()){
            $('#shelf').css({'left': 0});
          }
        }
      }
      app.triggerEvent('itemChanged', [id]);
    });
    // -- sound event
    $('.remove_snd').live('click', function(){
      $(this).parents('.ui-draggable').remove();
      app.triggerEvent('itemChanged', ['sound']);
      return false;
    });
   // -- overlay event [MODULES & COLLECTION]
	$('.overlay').live('click', function(){
		var id = $(this).siblings('a').attr('id');
		if (id !== "") {
			app.helpers.displayDetails(app.data.files[id.substr(5)], false);
		} else
		id = $(this).parent().attr('id');
		var obj = app.data.map[id];
		var segment = obj.id;
		// -- already loaded modules has got defined language, else load module
		if (obj.language !== undefined ) {
			app.helpers.displayDetails(app.data.map[id],false);
		} else {
			var url = '/content/segment/' + segment + "/";
	        $.get(
	        url,
	        function(data) {
	            app.data.map[id] = data;
	            app.helpers.displayDetails(app.data.map[id],false);
	        });
        }
	});
	   // -- roller item event
    $('.singleFile').live('click', function(){
        app.helpers.displayDetails(app.data.files[$(this).attr('id').substr(5)], false);
        $('#rollerItems li').removeClass('active');
        $(this).parent().addClass('active');
        return false;
    });

    // -- temporary events for title and objective
		var titleSearchDefault;
		titleSearchDefault = $('#c_title').val();
    $('#c_title').focus(function() {
    	if(titleSearchDefault == $('#c_title').val()) {
    		$('#c_title').val('');
    	}
    });
    $('#c_title').blur(function() {
    	if($('#c_title').val() == '') {
    		$('#c_title').val(titleSearchDefault);
    	}
    });

    $('#c_title').keyup(function(event){
        if($(this).val()) {
            clearTimeout(formTimer);
            formTimer = setTimeout('app.module.save()', 3000);
        }
    });
		$('#c_objective').keyup(function(event){
        if($(this).val()) {
            clearTimeout(formTimer);
            formTimer = setTimeout('app.module.save()', 3000);
        }
    });

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
    // -- collection manipulation functions -- //
    $('#shelfId').sb();
    $('#shelfId').change(function(){
        app.shelf.showShelf($(this).val());
    });
    $('#newCollection').hide();
    $('#collectionCreate').click(function(){
        $('#newCollection').show();
        $('#shelfTitle').focus();
        $('#collectionSelector').hide();
        return false;
    });
    $('#collectionEdit').click(function(){
    	$('#newCollection').show();
    	$('#shelfTitle').val($('#shelfId :selected').html());
    	$('#shelfTitle').focus();
    	$('#collectionSelector').hide();
    	app.data.change = true;
    	return false;
    })
    $('#collectionSave').click(function(){
        if($.trim($('#shelfTitle').val()) != ''){
        	if (app.data.change)
        	{
        		app.data.shelfId = $('#shelfId').val();
            app.shelf.save($('#shelfId').val());
        	}
        	else
        	{
         		app.data.shelfId = false;
           	app.shelf.save();
          }
        }
        $('#newCollection').hide();
        $('#collectionSelector').show();
        app.data.change = false;
        return false;
    });
    $('#collectionCancel').click(function(){
        $('#newCollection').hide();
        $('#collectionSelector').show();
        return false;
    });
    $('#collectionDelete').click(function(){
        app.helpers.window(
            t.SYSTEM_MESSAGE,
            t.SHELF_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
            [{
                'text': t.YES,
                events: [{
                    name: 'click',
                    handler: function() {
                        app.shelf.remove();
                        $.nmTop().close();
                        return false;
                    }
                }]
            },{
                'text': t.NO,
                events: [{
                    name: 'click',
                    handler: function() {
                        $.nmTop().close();
                        return false;
                    }
                }]
            },{
                'text': t.CANCEL,
                events: [{
                    name: 'click',
                    handler: function() {
                        $.nmTop().close();
                        return false;
                    }
                }]
            }],
            false
       );
       return false;
    });
    $(app).bind('moduleSaved', function(){
       if(app.data.doneClicked){
           document.location.href = '/content/#' + app.data.moduleId;
       }
    });
    $('#doneButton').click(function() {
       if (!$(app.config.moduleTitle).val()) {
            app.helpers.window(t.SYSTEM_MESSAGE, t.TITLE_IS_REQUIRED);
            return false;
       }

       if ($(app.config.moduleTitle).val().length > 30) {
            app.helpers.window(t.SYSTEM_MESSAGE, t.TITLE_CAN_BE_MAX_30_LETTERS_LONG);
            return false;
       }

       app.data.doneClicked = true;

       //console.log(app.data.moduleId);
       if(app.data.moduleId) {
           app.module.save();
           app.helpers.throbber('#createModule');

       }/* else {
           app.data.doneClicked = false;
           app.helpers.window(t.SYSTEM_MESSAGE, t.NO_CHANGES_MADE);
       }*/
       return false;
    });

    $(".collapsible label").click(function () {
        $(this).parents(".collapsible").toggleClass("collapsed");
        $('#shelfId').sb('refresh');
        //app.triggerEvent('itemChanged', [$('.shelf').attr('id')]);
    });

    addSortable();
    addDraggable();

    $('.shelf').each(function() {
    	var elements = $(this).find('li').length;
      var container = $(this).parent();
		if (elements < 6) {
			$(container).siblings(".prev, .next").addClass('disabled');
		} else {
			$(container).siblings(".prev, .next").removeClass('disabled');
		}
	});
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

    //hiding Shelf after it loaded
    $(".collapsible").addClass("collapsed");

});
var searchDefault;
function submitSearch(){
    clearTimeout(formTimer);
    formTimer = setTimeout("if ( $('#id_file_name').val() == searchDefault ) { $('#id_file_name').val(''); $('#search').submit(); $('#id_file_name').val(searchDefault); } else { $('#search').submit(); }", 1000);
}
