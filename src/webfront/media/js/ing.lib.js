/**
 * New method in function's object prototype. Allows to find object's instance within
 * the DOM. It iterates through every node of DOM, thus the desired element should be
 * as high in the DOM hierarchy as possible.
 *
 * Warning: This function returns ONLY
 * the first instance of desired object.
 */
Function.prototype.findInDOM = function() {
    return window['app'];
}

/**
 * Elements unique method. Ads possibility to check if listener
 * for specific event has been attached to particular element.
 * Uses jquery _data and works only with jquery defined events.
 */
if (typeof Element.hasEventListener != "function") {
	Element.prototype.hasEventListener = function(eventName) {
		var events = $._data(this, "events");
		for(var elEvent in events) {
			if (elEvent == eventName) 
				return true;
		}
		return false;
	};
}

/**
 * Allows using keys function across older browser
 */
var getObjKeys = function(object) {
	var keys = [];
	if (typeof object == "object"){
		for(var key in object) {
			keys.push(key);
		}
		return keys;
	}
};

var swfobject;
var closeSent = false;

/**
 * Array.unique method. Returns an array without duplicate values.
 */
Array.prototype.unique = function() {
    var a = [];
    var l = this.length;
    for(var i=0; i<l; i++) {
        for(var j=i+1; j<l; j++) {
            if (this[i] == this[j])
                j = ++i;
        }
        a.push(this[i]);
    }
    return a;
}
/**
 * Array.inArray method. Returns true if element
 * has been found within an array.
 */
Array.prototype.inArray = function(v) {
    for(var i in this) {
        if(this[i] == v) {
            return true;
        }
    }
    return false;
}

// Add ECMA262-5 string trim if not supported natively
//
if (!('trim' in String.prototype)) {
    String.prototype.trim= function() {
        return this.replace(/^\s+/, '').replace(/\s+$/, '');
    };
}

// Add ECMA262-5 Array methods if not supported natively
// {{{
if (!('indexOf' in Array.prototype)) {
    Array.prototype.indexOf= function(find, i /*opt*/) {
        if (i===undefined) i= 0;
        if (i<0) i+= this.length;
        if (i<0) i= 0;
        for (var n= this.length; i<n; i++)
            if (i in this && this[i]===find)
                return i;
        return -1;
    };
}

if (!('filter' in Array.prototype)) {
    Array.prototype.filter= function(filter, that /*opt*/) {
        var other= [], v;
        for (var i=0, n= this.length; i<n; i++)
            if (i in this && filter.call(that, v= this[i], i, this))
                other.push(v);
        return other;
    };
}
// }}}

/**
 * Object size function. Returns number of object's fields.
 */
function objSize(obj) {
    var size = 0;
    for(key in obj) {
        if(obj.hasOwnProperty(key)) {
            size++;
        }
    }
    return size;
}

//if (!!window.siteLanguage) $.get('/media/xml/messages_'+siteLanguage+'.xml', {}, function(data){
//	var messages = {};
//	$(data).find('message').each(function() {
//		messages[$(this).attr('varname')] = $(this).text();
//	});
//	if (!!objSize(messages)) t = $.extend(t, messages);
//});

/**
 * Global ajax error handler
 *
 * Warning: This is a beta version of the handler
 */
$(document).ajaxError( function(event, xhr, settings, error) {
    Ing.findInDOM().helpers.window(
    'An exception has occured',
    'Requested URL: ' + settings.url + '<br />' +
    'Status code: ' + xhr.status + '<br />' +
    'Response: ' + xhr.responseText + '<br />' +
    'Error: ' + error);
});
/**
 *
 * Default Ingine aplication and namespace
 *
 * @see http://flowplayer.org/tools/scrollable/index.html   - scroller    (roller, shelf)
 * @see http://docs.jquery.com/UI/Sortable                  - sorter      (shelf)
 * @see http://docs.jquery.com/UI/Draggable                 - drag&drop   (roller)
 * @see http://nyromodal.nyrodev.com/                       - modal win   (flash player)
 * @see http://www.json.org/js.html                         - JSON serializing methods by Douglas Crockford
 */

function Ing() {
    /**
     * Configuration object
     */
    this.config = {
        'ocl_token': '',
        'cookieTime':    3600,
        'elemWidth':     107,
        'elemWrapperWidth': 139,
        'fileId':        '#fileID',
        'fileIdVal':     0,
        'modal':         {
            'height': 500,
            'width': 700
        },
        'module':        '#module',
        'moduleTitle':   '#c_title',
        'moduleObjective': '#c_objective',
        'nextURL':       '/content/files/',
        'other':         {
            'movingStep': 20,
            'movingInterval': 40,
            'ml': '#moduleLeft',
            'mr': '#moduleRight',
            'sl': '#shelfLeft',
            'sr': '#shelfRight',
            'timer': false,
            'timer2': false
        },
        'player':        {
            'splash': '.nm',
            'minFlashVersion': "9.0.0",
            'mode': 'flash',
            'flashPlayer': {
                'url': 'swf/player.swf',
                'params': {
                	'allowFullscreen': 'true',
                	'allowScriptAccess': 'always',
                	'wmode': 'transparent'
                }
            },
            'html5player': {
            	'mp4_support': "",
	    		'webM_support': "",
	    		'theora_support': "",
	    		'canvas_support': false
    		},
            'modalSize': {'width': 700, 'height': 500},
            'embedSize': {'width': 600, 'height': 480},
            'zIndex': 15000
        },
        'roller':        '#roller',
        'rollerNavi':    '.navi',
        'searchForm':    '#search',
        'searchInput':   '#id_file_name',
        'languageInput':   '#id_language',
        'fileTypeInput':   '#id_file_type',
        'myFilesInput':  '#my',
        'inactiveFilesInput':  '#ia',
        'fromMyGroups':  '#from_my_groups',
        'shelf':         '#shelf',
        'shelfWrapperWidth': 780,
        'sound':         '.sound',
        'soundId':       '#sound',
        'soundFile':     '.snd',
        'tagsInput':     '#id_tags_ids',
        'tagList':       '#tagList',
        'totalFilesCount': '#totalFiles',

    },
    /**
     * Main function - starts the app
     */
    this.run = function() {
        this.checkHTML5Features();
        if (this.config.player.mode == "flash") {
            if(swfobject.hasFlashPlayerVersion("9.0.115")){
            	
            } else {
            	alert("You do not have the minimum required flash version. Please install Flash and come back. http://get.adobe.com/flashplayer/ ");
            }
        }
        if (typeof MediaPlayer === typeof Function) {
        	this.player = new MediaPlayer(this);
        }
        this.listeners.changeListener();
        this.listeners.tagsListener();
        this.listeners.formSubmitListener();// -- IE bug
        this.player.init();
        this.helpers.tools();
        this.data.files = [];
        this.data.map = {};
        
        window.onorientationchange = function() {
        	$(window).resize();
        	if ($('#video.fullscreen').length)
        		$('#video').trigger('onscreenrotate');
        }
    },
    
    /**
     * This method performs all HTML5 features detection logic
     * and stores results in application config. HTML5/Flash player 
     * bases on those results.
     */    
    this.checkHTML5Features = function() {
    	var playerConfig = this.config.player,
    		testVideo = document.createElement('video'),
    		testCanvas = document.createElement('canvas'),
    		testAudio = document.createElement('audio');
    	
    	playerConfig.mode = (!!testVideo.canPlayType && !!testCanvas.getContext && !!testAudio.canPlayType) ? "html5": "flash";
    	if (playerConfig.mode == "html5") {
    		playerConfig.html5player.mp4_support = testVideo.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
    		playerConfig.html5player.webM_support = testVideo.canPlayType('video/webm; codecs="vp8, vorbis"');
    		playerConfig.html5player.theora_support = testVideo.canPlayType('video/ogg; codecs="theora, vorbis"');
    		playerConfig.html5player.mp3_support = testAudio.canPlayType('audio/mpeg');
    		playerConfig.html5player.ogg_support = testAudio.canPlayType('audio/ogg');
    		playerConfig.html5player.canvas_support = (typeof testCanvas.getContext('2d').fillText === typeof Function);
    	}
		playerConfig.html5player.webkit_fullscreen_support = (!!testVideo.webkitRequestFullScreen);
		playerConfig.html5player.moz_fullscreen_support = (!!testVideo.mozRequestFullScreen);
		playerConfig.html5player.standard_fullscreen_support = (!!testVideo.requestFullscreen);
		playerConfig.html5player.fullscreen_support = playerConfig.html5player.webkit_fullscreen_support 
													|| playerConfig.html5player.moz_fullscreen_support 
													|| playerConfig.html5player.standard_fullscreen_support;
		
		playerConfig.html5player.touch_support = ('ontouchstart' in document.documentElement
												   || 'ontouchend' in document.documentElement
												   || 'ontouchmove' in document.documentElement);
    },
    /**
     * Callback functions - every callback sent to or
     * received from flash player, HTML player,
     * SCORM player or backend.
     */
    this.callbacks = {
        parent: this,
        /**
         * Handles search form submit
         */
        handleFormSubmit: function(event) {
            var cnf = this.parent.config;
            event.preventDefault();
            if($(cnf.tagsInput).val() != '') {
                var tmp = $.Event('keyup');
                tmp.keyCode = 13;
                $(this.parent).trigger(tmp);
            }
            if(!(this.parent.data.tags)) {
                this.parent.data.tags = [];
            }
            var tags = [];
            for(var i = 0, len = this.parent.data.tags.length; i < len; i++) {
                tags.push(encodeURIComponent(this.parent.data.tags[i].name));
            }
            this.parent.data.nextURL = this.parent.config.nextURL+ '?' + 'tags_ids='
            + tags.join(',')
            + '&file_name=' + $(cnf.searchInput).val()
            + '&language=' + $(cnf.languageInput).val()
            + '&file_type=' + $(cnf.fileTypeInput).val()
            + '&my_files=' + $(cnf.myFilesInput + ':checked').length
            + '&inactive_files=' + $(cnf.inactiveFilesInput + ':checked').length
            + '&from_my_groups=' + $(cnf.fromMyGroups + ':checked').length;
            this.parent.loadFiles(false);
            return false;
        },
        /**
         * Opens message modal with parameters
         */
        openCompose: function(recipientsNames, recipientsIds, subject, course_id) {
            this.parent.callbacks.openMessageForm(recipientsNames, recipientsIds, '/messages/compose/', subject, course_id);
        },
        openReply: function(recipientName, recipientId, messageid) {
            this.parent.callbacks.openMessageForm(recipientName, [recipientId], '/messages/reply/' + messageid + '/');
        },
        openMessageForm: function(recipientsNames, recipientsIds, url, subject, course_id) {
            $('<a href="' + url + '" />').nyroModal({
                callbacks: {
                    afterReposition: function(nm) {
                        Ing.findInDOM().triggerEvent('msgformOpened');
                        $("#recipients").html(recipientsNames.toString());
                        $('#recipients_ids').val(recipientsIds.toString());
                        $('#course_id').val(course_id);
												if (subject) {
														subject = subject.replace(/^\s+|\s+$/g, '')
												}
												$("#id_subject").val(subject);

                        $('#sendMessage').bind('click', function(event) {
                            if($.trim($('#id_body').val()) != '' && $.trim($('#id_subject').val()) != '') {
                                $.post(
                                url,
                                JSON.stringify({
                                    "subject": $("#id_subject").val(),
                                    "body": $("#id_body").val(),
                                    "recipients": $('#recipients_ids').val().split(','),
                                    "course_id": $('#course_id').val()
                                }), function(data, status, xmlHttpRequest) {
                                    if(data.status == "OK") {
                                        $('.nyroModalClose').trigger('click');
                                        $('input:checked').removeAttr('checked');
                                        $('.noMails').text(0);
                                    } else {
                                        //TODO handler error
                                        $('.nyroModalClose').trigger('click');
                                        $('input:checked').removeAttr('checked');
                                        $('.noMails').text(0);
                                    }
                                });
                            } else {
                                $('.formError').remove();
                                if($.trim($('#id_body').val()) == '') {
                                    $('#id_body').parent('div').after('<div class="formError"><div class="hr"></div>' + t.FIELD_CANNOT_EMPTY + '</div>');
                                }
                                if($.trim($('#id_subject').val()) == '') {
                                    $('#id_subject').parent('div').after('<div class="formError"><div class="hr"></div>' + t.FIELD_CANNOT_EMPTY + '</div>');
                                }
                                $.nmTop().resize(true);
                            }
                            return false;
                        });
                        $('#cancelMessage').bind('click', function(event) {
                            $('.nyroModalClose').trigger('click');
                        });
                    }
                }
            }).trigger('click');
        },
        /**
         * Handles display of entered tags
         *
         * Function overrriden due to functionality change
         */
        handleTags: function (elem, event, tagList) {
            if(event){
                if(typeof event === 'string'){
                    tagList = event;
                    event = undefined;
                }
            }
            if($(elem) && (!event || event.keyCode == 13)) {
                if(!(this.parent.data.tags)) {
                    this.parent.data.tags = [];
                }
                var cnf = this.parent.config;
                var els = this.parent.elements;
                var tgs = this.parent.data.tags;
                if($(elem).is('select')) {
                    var tag = $.trim($(elem + ' option:selected').text());
                } else {
                    var tag = $.trim($(elem).html()) || $.trim($(elem).val());
                }
                $(elem).val('');
                if(tag.length > 30) {
                    this.parent.helpers.window(t.SYSTEM_MESSAGE, t.TAG_NAME_MAX_LONG);
                    return false;
                }
                var exists = tag == '';
                for(var j = 0, ln = tgs.length; j < ln; j++) {
                    if($.trim(tgs[j].name).toLowerCase() == $.trim(tag).toLowerCase()) {
                        exists = true;
                    }
                }
                if(!tagList){
                    tagList = cnf.tagList;
                }
                if(!exists) {
                    tgs.push({name: tag});
                    var el = new els.tag(tag);
                    els.attach(el, tagList);
                    if(this.parent.config.searchForm) {
												$('#id_file_name').val('');
                        $(this.parent).trigger($.Event('submit_search'));
                    }
                }
            }
        },
        /**
         * Handles removing tags from an internal array
         */
        handleTagRemoval: function(event, tag) {
            var tgs = this.parent.data.tags;
            for(var i = 0, len = tgs.length; i < len; i++) {
                if(tgs[i].name == tag) {
                    tgs.splice(i, 1);
                    if(this.parent.config.searchForm) {
												$('#id_file_name').val('');
                        $(this.parent).trigger($.Event('submit_search'));
                    }
                    return true;
                }
            }
            return false;
        },
        /**
         * Saves changes made to a shelf or a module
         *
         * @todo: Write saving for shelf
         */
        saveChanges: function(id) {
            var actions = {
                module: 'this.parent.module.save()',
                sound: 'this.parent.module.save()',
                shelf: 'this.parent.shelf.save()'
            }
            if(actions[id]) {
                eval(actions[id]);
            }
        },
        /**
         * Saving module. Sending module as a JSON object
         * to a backend saving script.
         *
         */
        saveModule: function(json) {
            if(!(this.parent.data.saving)) {
                this.parent.data.saving = true;
                var url = '/content/save/';
                var json = JSON.stringify(json);
                $.post(
                url,
                json, function(data) {
                    var ing = Ing.findInDOM();
                    if(!(ing.data.moduleId)) {
                        if(data.meta.id) {
                            ing.data.moduleId = data.meta.id;
                        }
                    }
                    ing.triggerEvent('moduleSaved');
                    ing.data.saving = false;
                }
                );
                this.parent.helpers.js_notify('<b>Saving module:</b> ' + json, 'info');
            }
        },
        /**
         * Saving shelf. Sending shelf as a JSON object
         * to a backend saving script.
         *
         */
        saveShelf: function(json) {
            if(!(this.parent.data.savingShelf)) {
                this.parent.data.savingShelf = true;
               	var url = '/content/collections/save/';
                if(this.parent.data.shelfId){
                    url += this.parent.data.shelfId + '/';
                }
                var json = JSON.stringify(json);
                $.post(
                    url,
                    json, function(data) {
                        var ing = Ing.findInDOM();
                        if(data.id) {
                            ing.data.shelfId = data.id;
                        }
                        ing.shelf.loadShelfs(ing.data.shelfId);
                        ing.data.savingShelf = false;
                });
            }
        },
        /**
         * media player callbacks
         */
        mp: {
            parent: this,
            /**
             * Handler for error messages.
             */
            error_handler: function(msg) {
                this.parent.helpers.js_notify(msg, 'error');
            },
            /**
             * Handler for information messages.
             */
            info_handler: function(msg) {
            	var json,
            		ing = Ing.findInDOM();
					
                if (!moduleID) {
                	if (msg != "PLAYLIST_COMPLETE")
                    	return false;
                }

                try {
					json = $.parseJSON(msg);
				} catch(err) {
					json = false;
				}  

                if (json && json.segment_id) {
                    json.lesson_status = '';
                    switch(json.event_type) {
                        case 'START':
                            $.post(
                            '/tracking/events/create/?token='+app.config.ocl_token,
                            JSON.stringify(json), function(data) {
                                ing.data.lastEventId = data.event_id;
                                if(ing.data.lastEvent) {
                                    json = ing.data.lastEvent;
                                    json.parent_event_id = ing.data.lastEventId;
                                    if(json.event_type == 'LEAVING') {
                                        ing.data.lastEventId = false;
                                        json.event_type = 'END';
                                    }
                                    ing.data.lastEvent = false;
                                    $.post(
                                    '/tracking/events/create/?token='+app.config.ocl_token,
                                    JSON.stringify(json), function(data) {
                                        if(json.lesson_status == 'completed'){
                                            var map = Ing.findInDOM().data.map;
                                            $.each(map, function(key, value){
                                               if(value.segment_id == json.segment_id){
                                                   $('#'+key).addClass('completed');
                                                   if(this.allow_downloading == true && !($('#'+key).has(':button.segmentDownload').length)) {
                                                    var ocl_token = Ing.findInDOM().config.ocl_token;
                                                    var download_url = value.download_url;
                                                    if (ocl_token) {
														if (download_url.indexOf('?token=') < 0)
                                                        	download_url += '?token=' + ocl_token;
                                                    }
                                                       $('#'+key).append(' <button class="segmentDownload" onclick="window.location.href=\''+download_url+'\'" title="' + t.SEGMENT_DOWNLOAD + '"></button>');
                                                   }
                                                   $('#'+key).next().find('.courseApla').remove();
                                                   return false;
                                               }
                                            });
                                            $('#video').trigger('segmentCompleted');
                                            app.module.showHideSignOffButton(moduleID);
                                        }
                                    }
                                    );
                                }
                            }
                            );
                            break;
                        case 'END':
                            json.lesson_status = 'completed';
                            if(ing.data.lastEventId) {
                                json.parent_event_id = ing.data.lastEventId;
                                ing.data.lastEvent = false;
                                $.post(
                                    '/tracking/events/create/?token='+app.config.ocl_token,
                                    JSON.stringify(json),
                                    function(data) {
                                     if(json.lesson_status == 'completed'){
                                            var map = Ing.findInDOM().data.map;
                                            $.each(map, function(key, value){
                                               if(value.segment_id == json.segment_id){
                                                   $('#'+key).addClass('completed');
                                                   if(this.allow_downloading == true && !($('#'+key).has(':button.segmentDownload').length)) {
                                                        var ocl_token = Ing.findInDOM().config.ocl_token;
                                                        var download_url = value.download_url;
                                                        if (ocl_token) {
															if (download_url.indexOf('?token=') < 0)
                                                            	download_url += '?token=' + ocl_token;
                                                        }
                                                       $('#'+key).append(' <button class="segmentDownload" onclick="window.location.href=\''+download_url+'\'" title="' + t.SEGMENT_DOWNLOAD + '"></button>');
                                                   }
                                                   $('#'+key).next().find('.courseApla').remove();
                                                   return false;
                                               }
                                            });
                                            $('#video').trigger('segmentCompleted');
                                            app.module.showHideSignOffButton(moduleID);
                                        }
                                    }
                                );
                            } else {
                                ing.data.lastEvent = json;
                            }
                            break;
                        case 'PAGE':
                        	if(ing.data.lastEventId) {
	                        	json.parent_event_id = ing.data.lastEventId;
	                            $.post('/tracking/events/create/?token='+app.config.ocl_token, JSON.stringify(json));
                        	}
                        	break;
                        case 'LEAVING':
                            if(ing.data.lastEventId) {
                                json.parent_event_id = ing.data.lastEventId;
                                ing.data.lastEventId = false;
                                ing.data.lastEvent = false;
                                json.event_type = 'END';
                                $.post(
                                '/tracking/events/create/?token='+app.config.ocl_token,
                                JSON.stringify(json), function(data) {
                                    app.module.showHideSignOffButton(moduleID);
                                }
                                );
                            } else {
                                ing.data.lastEvent = json;
                            }
                            break;
                        default:
                            break;
                    }					
					/* Handle click on player close button */
					$(".close").click(function(event) {
						event.preventDefault();
						var closeLink = $(this);
						if(ing.data.lastEventId) {
							json.parent_event_id = ing.data.lastEventId;
							ing.data.lastEventId = false;
							ing.data.lastEvent = false;
							json.event_type = 'LEAVING';
							$.ajax({
								type: 'POST',
								url: '/tracking/events/create/?token='+app.config.ocl_token,
								data: JSON.stringify(json),
								timeout: 2000,
								success: function(data) {
									app.module.showHideSignOffButton(moduleID);
									closeSent = true;
									window.location.href = closeLink.attr('href');
								},
								async: false
							});
						} else {
							ing.data.lastEvent = json;
							window.location.href = closeLink.attr('href');
						}
					});
					/* Send tracking data on exit */
					window.onbeforeunload = function() {
						if(!closeSent) {
							json.parent_event_id = ing.data.lastEventId;
							ing.data.lastEventId = false;
							ing.data.lastEvent = false;
							json.event_type = 'LEAVING';
							$.ajax({
								type: 'POST',
								url: '/tracking/events/create/?token='+app.config.ocl_token,
								data: JSON.stringify(json),
								timeout: 2000,
								success: function(data){ app.module.showHideSignOffButton(moduleID); },
								async: false
							});
						}
					}
                } else if (ing.config.player.mode == "flash" && msg.trim() == "PLAYLIST_COMPLETE") {
                	var msgBody,
                		module,
                		controlsTimer,
                		goodbyeMsg = document.createElement('div'),
                		playerPrev = document.createElement('div'),
                		playerContainer = (!!document.getElementById('videoWrapper'))? document.getElementById('videoWrapper'): $('.mplayerWrapper')[0];
                		
                	if (!!ing.data.moduleJSON) {
                		module = ing.data.moduleJSON;
                	} else if (!$('#modulesPreviewList').length) {
                		module = ing.data.modules[ing.data.activeModule.id];
                	} else {
                		module = ing.data.modules[parseInt($('#modulesPreviewList').find('.selected').attr('id').replace(/_/, ''))];
                	}
                		
                	if (playerContainer === undefined)
                		playerContainer = $('#assignmentPreviewLesson')[0];
                		
                	playerPrev.setAttribute('class', 'goBack');
			    	playerPrev.setAttribute('id', 'goBack');
			    	playerPrev.setAttribute('style', 'z-index: 102;');
	        		goodbyeMsg.setAttribute('id', 'flashCustomMsg');
	        		msgBody = '<div class="goodbyeMsg"><div class="messageBody">'; 
	        		msgBody += (!!module.meta.completion_msg)? ing.helpers.htmlSpecialDecoder(module.meta.completion_msg): t.LESSON_FINISHED;
	        		msgBody += '</div></div>';
	        		$('#videoWrapper').css('position', 'relative');
	        		playerContainer.appendChild(goodbyeMsg);
	        		playerContainer.appendChild(playerPrev);
	        		$(goodbyeMsg).html($(msgBody));
	        		$(goodbyeMsg).css({'height': $(playerContainer).find('object').height()});
	        		$(goodbyeMsg).find('.goodbyeMsg').css('top', ($(playerContainer).find('object').height() - $(goodbyeMsg).find('.messageBody').outerHeight())/2);
					$('.goBack').one('click', function(event){
		        		event.preventDefault();
		        		ing.player.api.play(module.track0.length - 1);
		        	});
		        	$(goodbyeMsg).on('mousemove', function(){
		        		$('.goBack').show();
				    	clearTimeout(controlsTimer);
				    	controlsTimer = setTimeout(function(){
				        	$('.goBack').hide()
				    	}, 2000);
		        	});
                }
            },
            /**
             * Handler for flash player exceptions.
             */
            exception_handler: function(msg) {
                this.parent.helpers.js_notify(msg, 'exception');
            },
            /**
             * Handler for keypress events.
             */
            keypress_handler: function(keyCode) {
                var msg = 'key pressed! (code: ' + keyCode + ', key: ' + this.parent.helpers.cc(keyCode) + ')';
                this.parent.helpers.js_notify(msg, 'notice');
            },
            /**
             * Handler for mouseclick events.
             */
            click_handler: function(url) {
                window.open(url);
                this.parent.helpers.js_notify('External URL displayed: ' + url, 'notice');
            },
            /**
             * Handler for displaying PDF files
             */
            pdf_handler: function(url, pages) {
                var nextButton,
                	prevButton,
                	currentPage,
                	title,
                	itemsList,
                	canSkip,
                	segment_id = 0;
                
                if(pages === undefined || pages == 0) {
                    var pages = 1;
                }
                if(this.parent.data.moduleJSON){
                    var mod = this.parent.data.moduleJSON.track0;
                    for(var i = 0, len = mod.length; i < len; i++){
                        if(mod[i].start == this.parent.data.activeItem){
                            //console.log(mod[i].segment_id);
                            segment_id = mod[i].segment_id;
                            break;
                        }
                    }
                }
                var els = this.parent.elements;
                var ing = this.parent;
                
                if (!!ing.player.playlist) {
                    title = ing.player.playlist[(!!ing.data.activeItem)? ing.data.activeItem: ing.player.playlistParams.playingIndex].title;                	
                } else title = $('#rollerItems li.active').attr('title'); 
                
                if (ing.config.player.mode == "html5") {
                	var p = els.getObj(new els.playerHTML5({'src': url + '/p-1.html', 'title': title})),
			        	id = p.attr('id'),
			        	currentPage;
                	
			    	p.appendTo('#video');
	                nextButton = $('.goAhead');
	                prevButton = $('.goBack');

			    	$('.playerHTML5').addClass('playerSCORM');
			        p.css({
			            'height':  $('#video').height() + 'px',
			            'width':  $('#video').width() + 'px'
			        });
			        p.find('.playerHTML5').css({
			            'height':  ($('#video').height() - 26) + 'px',
			            'width':  $('#video').width() + 'px'
			        });
			        p.find('iframe').css({
			            'border': 'none'
			        });
			        
			        $('.playerHTML5 iframe').load(function() {
			        	$('.playerHTML5 iframe').contents().find('img').css('-webkit-transform', 'translateZ(0)');
			        });
			              
                    itemsList = $('#moduleList').find('li');
                    
                    if (itemsList.length && !!ing.player.playlistParams) {
                        if (itemsList.length >= ing.player.playlistParams.playingIndex + 1) {
                        	canSkip = $(itemsList[ing.player.playlistParams.playingIndex + 1]).find('.courseApla').length < 1
                    					|| ing.player.playlist[ing.player.playlistParams.playingIndex + 1].allow_skipping
                    					|| ing.player.playlist[ing.player.playlist.length -1].is_learnt;
                    	} else canSkip = (ing.player.playlistParams.playingIndex < ing.player.playlist.length);
                        if (canSkip)
                        	$('.skipTo').toggleClass('hidden', false);
                    }else if (!ing.player.trackUser && !!ing.player.playlistParams) {
                    	$('.skipTo').toggleClass('hidden', false);                    	
                    }
                    
                    $('.skipTo:not(.hidden)').click(function(event){
                    	event.preventDefault();
        	    		$('.goAhead').unbind('click');
        	    		$('.goBack').unbind('click');
        	    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex + 1]);
                    });
			        
			        currentPage = $('.playerHTML5 iframe').attr('src').match(/p-([0-9]+)/);
                    $(window).resize(function(){
                        if(TO !== false)
                            clearTimeout(TO);
                        TO = setTimeout(resizeThisModal, 50);
                    });
                    //resizing image content to fit modal window
                    checkImage = setTimeout(checkImageWidth, 150);
                } else {
	                var p = els.getObj(new els.playerHTML({'src': url + '/p-1.html'})),
	                	id = p.attr('id');
	                
	                p.appendTo('body');
	                nextButton = $('.playerNext, .goAhead');
	                prevButton = $('.playerPrev, .goBack');
	                
	                p.children('div').css({
	                    'height':  ($(window).height() - 20) + 'px',
	                    'width':  $(window).width() + 'px'
	                });
	                p.find('iframe').css({
	                    'height':  ($(window).height() - 115) + 'px',
	                    'width':  ($(window).width() - 50) + 'px'
	                });
	                $('<a href="#' + id + '" />').nyroModal({
	                    callbacks: {
	                        afterClose: function(nm) {
	                            $('#' + id).remove();
	                            // -- adding leaving event
	                            if(segment_id){
	                                ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'LEAVING', 'segment_id': segment_id}));
	                            }
	                        },
	                        beforeShowCont: function(nm) { //hiding iframe before repositioning images
	                            $(".nyroModalCont iframe").css("visibility","hidden");
	                        },
	                        afterShowCont: function(nm) {
	                            $(window).resize(function(){
	                                if(TO !== false)
	                                    clearTimeout(TO);
	                                TO = setTimeout(resizeThisModal, 50);
	                            });
	                            //resizing image content to fit modal window
	                            checkImage = setTimeout(checkImageWidth, 150);
	                        }
	                    }
	                }).trigger('click');
	
	                	
	                currentPage = $('.playerPages').siblings('iframe').attr('src').match(/p-([0-9]+)/);
                }
                var TO = false;
                function resizeThisModal() {
                    $(".nyroModalCont iframe").width( $(window).width()-25 ).height( $(window).height()-115 );
                    $(".nyroModalCont .playerHTML").width( $(".nyroModalCont iframe").width()+25 ).height( $(".nyroModalCont iframe").height()+95 );
                    setTimeout("if ($.nmTop()) { $.nmTop().resize(true) }", 150);
                }

                function checkImageWidth() { //repositioning images in the iframe
                    if (checkImage) {
                        clearTimeout(checkImage);
                    }
                    var img = $(".playerHTML iframe").contents().find("img");
                    var imgWidth = img.width();
                    var imgHeight = img.height();
                    if ( imgWidth > 30 ) {
                        if ( imgWidth > imgHeight ) {
                            img.css("max-height",imgHeight+"px").css("height","100%").css("margin","0 auto").css("display","block");
                            // fixing IE display bug
                            if ( $.browser.msie && $.browser.version < 9 ) {
                                var newImgWidth = img.width();
                                img.css("position","absolute").css("left","50%").css("margin-left","-"+newImgWidth/2+"px");
                            }                            
                        }
                        else {
                            img.css("max-width",imgWidth+"px").css("width","100%").css("margin","0 auto").css("display","block");
                            // fixing IE display bug
                            if ( $.browser.msie && $.browser.version < 9 ) {
                                var newImgWidth = img.width();
                                img.css("position","absolute").css("left","50%").css("margin-left","-"+newImgWidth/2+"px");
                            } 
                        }                        
                        $(".nyroModalCont iframe").css("visibility","visible").show();
                    }
                    else {
                        checkImage = setTimeout(checkImageWidth, 150);
                    }
                    return imgWidth;
                }

                // -- adding start event
                if(segment_id){
                    ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'START', 'segment_id': segment_id,
                    											  'page_number': parseInt(currentPage[1])}));
                }
                if(pages == 1){
                    // -- adding end event
                    if(segment_id){
                        ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
                    }
                }
                prevButton.on('click', function() {
                    var index = $('.playerHTML iframe').attr('src').match(/p-([0-9]+)/);
                    
                    if (parseInt(index[1]) == 1) {
                        if (ing.config.player.mode == "html5") {
                        	if (!!ing.player.playlistParams){
	        	    			$('.goAhead').unbind('click');
	        	    			$('.goBack').unbind('click');
	            	    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex - 1]);
	            	    	}
            	    	} else {
	         	    		$('.goAhead').unbind('click');
	        	    		$('.goBack').unbind('click');       	    			
        	    		}
        	    		return;
                    }
                    
                    if (parseInt(index[1]) > 1) {
                        ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'PAGE', 'segment_id': segment_id,
							  'page_number': parseInt(index[1]) - 1}));
                        $('.playerHTML iframe').attr('src',
                        	$('.playerHTML iframe').attr('src').replace(index[0], 'p-' + (parseInt(index[1]) - 1))
                        );
                        $('#pdf_cp').html(parseInt($('#pdf_cp').html()) - 1);
                    }
                    
                    //resizing image content to fit modal window
                    if ( !$('.playerPrev').hasClass("disabled") ) {
                        $(".nyroModalCont iframe").css("visibility","hidden");
                    }                    
                    $(".playerHTML iframe").one('load', function(){                        
                        checkImage = setTimeout(checkImageWidth, 100);
                    })
                    
                    if (pages != 1) {
                        if (index[1]-1 == 1) {
                            if (ing.config.player.mode == "html5") {
                            	prevButton.toggleClass('disabled', !ing.data.activeItem);
                            } else prevButton.toggleClass('disabled', true);
                        }
                        else {
                            $('.playerNext').removeClass("disabled");
                        }
                    }
                    
                    if (parseInt(index[1]) <= pages && ing.config.player.mode == "html5" && !ing.player.playlistParams) {
                        $('.goAhead').toggleClass('disabled', false);
                    }

                    return false;
                });
                nextButton.on('click', function() {
                    var index = $('.playerHTML iframe').attr('src').match(/p-([0-9]+)/);

                    if (parseInt(index[1]) == pages) {
        	    		if (ing.config.player.mode == "html5") {
        	    			ing.player.preventBtnControl = false;
        	    			if (!!ing.player.playlistParams){
        	    				$('.goAhead').unbind('click');
	        	    			$('.goBack').unbind('click');
	        	    			if(segment_id)
	                                ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'LEAVING', 'segment_id': segment_id}));
        	    				$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex + 1]); 
        	    			}    			
        	    		} else {
	         	    		$('.goAhead').unbind('click');
	        	    		$('.goBack').unbind('click');       	    			
        	    		}
        	    		return;
                    }
                    
                    if(parseInt(index[1]) < pages) {
                        ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'PAGE', 'segment_id': segment_id,
                        											  'page_number': parseInt(index[1]) + 1}));
                        $('.playerHTML iframe').attr('src',
                        	$('.playerHTML iframe').attr('src').replace(index[0], 'p-' + (parseInt(index[1]) + 1))
                        );
                        $('#pdf_cp').html(parseInt($('#pdf_cp').html()) + 1);
                    }
                    if(parseInt(index[1]) == pages - 1) {
                        // -- adding end event
                        if (ing.config.player.mode == "html5" && !ing.player.playlistParams)
                        	$('.goAhead').toggleClass('disabled', true);
                        	
                        if(segment_id) {
                            ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
                        }
                    }
                    
                    //resizing image content to fit modal window
                    if ( !$('.playerNext').hasClass("disabled") ) {
                        $(".nyroModalCont iframe").css("visibility","hidden");
                    }
                    $(".playerHTML iframe").one('load', function(){                        
                        checkImage = setTimeout(checkImageWidth, 100);
                    })

                    if (pages != 1) {
                        if(index[1] == pages-1){
                            $('.playerNext').addClass("disabled");
                        }
                        else {
                        	prevButton.toggleClass('disabled', false);
                        }
                    }

                    return false;
                });
                //Play next/prevoius buttons
                prevButton.toggleClass('disabled', false);
                nextButton.toggleClass('disabled', false);
                
                if (parseInt(currentPage[1]) == 1) {
                    if (ing.config.player.mode == "html5") {
                    	prevButton.toggleClass('disabled', !ing.data.activeItem);
                    } else prevButton.toggleClass('disabled', true);
                }
                if (parseInt(currentPage[1]) == pages) {
                    $('.playerNext').addClass("disabled");
                }
                if (parseInt(currentPage[1]) == 0 && currentPage[1] == pages) {
                    $('.playerPrev, .playerNext').hide();
                }
                //Player pages
                $('.playerClose').html(t.CLOSE_WINDOW).click( function(e) {
                    e.preventDefault();
                    $(".playerHTML").hide();
                    $.nmTop().close();
                    $('.mplayerWrapper .closeFW.oneElement').trigger('click');
                    //$('.mplayerWrapper, .modalBg').remove();
                });                	
                $('.playerPages').html(t.PAGE + " <span id=\"pdf_cp\">" + currentPage[1] + "</span> " + t.PAGE_OF + " " + pages);
                this.parent.helpers.js_notify('PDF displayed: ' + url, 'notice');
            },
            /**
             * Handler for displaying SCORM files
             */
            scorm_handler: function(url) {
                var ing = Ing.findInDOM(),
                	title,
                	segment_id;
                
                if(ing.config.scormTTL && (new Date()).getTime() - ing.config.scormTTL.getTime() > 1500) {
                    ing.config.scormTTL = false;
                }
                
                if(!ing.config.scormTTL) {
                    var segment_id = 0;
                    if(this.parent.data.moduleJSON){
                        var mod = this.parent.data.moduleJSON.track0;
                        for(var i = 0, len = mod.length; i < len; i++){
                            if(mod[i].start == this.parent.data.activeItem){
                                segment_id = mod[i].segment_id;
                                break;
                            }
                        }
                    }
                    ing.config.scormTTL = new Date();
                    var els = this.parent.elements;
                    
                    if (!!ing.player.playlist) {
                    	title = ing.player.playlist[(!!ing.data.activeItem)? ing.data.activeItem: ing.player.playlistParams.playingIndex].title;                	
                    } else title = $('#rollerItems li.active').attr('title'); 
                    
                    if (ing.config.player.mode == "html5") {
						app.player.enterFullScreen(document.getElementById('video'));
                    	var p = els.getObj(new els.playerHTML5({'src': url,
        						'title': title})),
				        	id = p.attr('id'),
				        	playIndex = ing.player.playlistParams.playingIndex;

                    	if (!!ing.player.playlistParams) {
                    		$('.goBack').toggleClass('disabled', !ing.player.playlistParams.playingIndex);
                    		$('.goAhead').toggleClass('disabled', false);
    				    	$('.goBack').on('click', function(event){
    	        	    		$('.goAhead').unbind('click');
    	        	    		$('.goBack').unbind('click');
    	        	    		ing.player.preventBtnControl = false;
    	        	    		ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
    				    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex - 1]);
    				    	});
    				    	$('.goAhead').on('click', function(event){
    	        	    		$('.goAhead').unbind('click');
    	        	    		$('.goBack').unbind('click');
    	        	    		ing.player.preventBtnControl = false;
    	        	    		ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
    				    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex + 1]);
    				    	});    
                    	} else {
                    		ing.player.preventBtnControl = false;
                    		$('.goAhead').unbind('click');
	        	    		$('.goBack').unbind('click');
                    	}
                    	
				    	p.appendTo('#video');
				    	$('.playerHTML5').addClass('playerSCORM');
				        p.css({
				            'height':  $('#video').height() + 'px',
				            'width':  $('#video').width() + 'px'
				        });
				        p.find('.playerHTML5').css({
				            'height':  ($('#video').height() - 26) + 'px',
				            'width':  $('#video').width() + 'px'
				        });
				        p.find('iframe').css({
				            'border': 'none'
				        });                	
                    } else {
	                    var p = els.getObj(new els.playerSCORM({'src': url}));
	                    var id = p.attr('id');
	                    p.appendTo('body');
	                    p.children('div').css({
	                        'height':  ($(window).height() - 20) + 'px',
	                        'width':  $(window).width() + 'px'
	                    });
	                    p.find('iframe').css({
	                        'height':  ($(window).height() - 110) + 'px',
	                        'width':  ($(window).width() - 50) + 'px',
	                        'margin-left': '25px',
	                        'border': 'none'
	                    });
	                    $('<a href="#' + id + '" />').nyroModal({
	                        callbacks: {
	                            afterClose: function(nm) {
	                                $('#' + id).remove();
	                                // -- adding leaving event
	                                if(segment_id){
	                                    ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
	                                }
	                            },
	                            afterShowCont: function(nm) {
	                                $(window).resize(function(){
	                                    if(TO !== false)
	                                        clearTimeout(TO);
	                                    TO = setTimeout(resizeThisModalScorm, 50);
	                                });
	                            }
	                        }
	                    }).trigger('click');
	
	                    var TO = false;
	                    function resizeThisModalScorm() {
	                        $("#scormFrame").width( $(window).width()-25 ).height( $(window).height()-110 );
	                        $(".nyroModalCont .playerSCORM").width( $("#scormFrame").width()+25 ).height( $("#scormFrame").height()+90 );
	                        setTimeout("if ($.nmTop()) { $.nmTop().resize(true) }", 150);
	                    }
	
	                    $('.playerClose').html(t.CLOSE_WINDOW).click( function() {
	                        $('.mplayerWrapper .closeFW.oneElement').trigger('click');
	                        $(".playerSCORM").hide();
	                        $.nmTop().close();
	                        //$('.mplayerWrapper, .modalBg').remove();
	                    });
	                    //window.open(url);
                    }
                    // -- adding start event
                    if(segment_id){
                        ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'START', 'segment_id': segment_id, 'is_scorm': true}));
                        this.parent.helpers.js_notify('Displaying SCORM the cool way: ' + url, 'notice');
                    }
                }
                return false;
            },
            /**
             * Handler for displaying HTML files
             */
            html_handler: function(url) {
                var ing = Ing.findInDOM(),
                	segment_id,
                	title;
                
                if(this.parent.data.moduleJSON){
                    var mod = this.parent.data.moduleJSON.track0;
                    for(var i = 0, len = mod.length; i < len; i++){
                        if(mod[i].start == this.parent.data.activeItem){
                            segment_id = mod[i].segment_id;
                            break;
                        }
                    }
                }
                
                var els = this.parent.elements;
                // -- hack
                if(url.indexOf('.txt') != -1){
                    url = url.replace('/media/pub/', '/content/file/').replace('.txt', '/');
                }   
                
                if (!!ing.player.playlist) {
                	title = ing.player.playlist[(!!ing.data.activeItem)? ing.data.activeItem: ing.player.playlistParams.playingIndex].title;               	
                } else title = $('#rollerItems li.active').attr('title'); 
                
                if (ing.config.player.mode == "html5") {
                    var p = els.getObj(new els.playerHTML5({'src': url,
                    										'title': title})),
                    	id = p.attr('id');
                    
                	if (!!ing.player.playlistParams) {
                		$('.goBack').toggleClass('disabled', !ing.player.playlistParams.playingIndex);
                		$('.goAhead').toggleClass('disabled', false);
                    	$('.goBack').on('click', function(event){
            	    		$('.goAhead').unbind('click');
            	    		$('.goBack').unbind('click');
            	    		ing.player.preventBtnControl = false;
                    		ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
                    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex - 1]);
                    	});
            	    	$('.goAhead').on('click', function(event){
            	    		$('.goAhead').unbind('click');
            	    		$('.goBack').unbind('click');
            	    		ing.player.preventBtnControl = false;
            	    		ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
            	    		$('#video').trigger('goTo', [ing.player.playlistParams.playingIndex + 1]);
            	    	});
                	} else {
                		ing.player.preventBtnControl = false;
                		$('.goAhead').unbind('click');
        	    		$('.goBack').unbind('click');
                	}
                	
                	p.appendTo('#video');
                    p.css({
                        'height':  $('#video').height() + 'px',
                        'width':  $('#video').width() + 'px'
                    });
                    p.find('.playerHTML5').css({
                        'height':  ($('#video').height() - 26) + 'px',
                        'width':  $('#video').width() + 'px'
                    });
                    p.find('iframe').css({
                        'border': 'none'
                    });
                    
                    $('.playerHTML5 iframe').load(function() {
			        	$('.playerHTML5 iframe').contents().find('pre').css('-webkit-transform', 'translateZ(0)');
			        });
                } else {
                    var p = els.getObj(new els.playerHTML({'src': url})),
                    	id = p.attr('id');
                    p.appendTo('body');
                    p.children('div').css({
                        'height':  ($(window).height() - 20) + 'px',
                        'width':  $(window).width() + 'px'
                    });
                    p.find('iframe').css({
                        'height':  ($(window).height() - 110) + 'px',
                        'width':  ($(window).width() - 50) + 'px',
                        'margin-left': '25px',
                        'border': 'none'
                    });
                    $('<a href="#' + id + '" />').nyroModal({
                        callbacks: {
                            afterClose: function(nm) {
                                $('#' + id).remove();
                                // -- adding end event
                                if(segment_id){
                                    ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'END', 'segment_id': segment_id}));
                                }
                            },
                            afterShowCont: function(nm) {
                                $(window).resize(function(){
                                    if(TO !== false)
                                        clearTimeout(TO);
                                    TO = setTimeout(resizeThisModal, 50);
                                });
                            }
                        }
                    }).trigger('click');

                    var TO = false;
                    function resizeThisModal() {
                        $(".nyroModalCont iframe").width( $(window).width()-25 ).height( $(window).height()-110 );
                        $(".nyroModalCont .playerHTML").width( $(".nyroModalCont iframe").width()+25 ).height( $(".nyroModalCont iframe").height()+90 );
                        setTimeout("if ($.nmTop()) { $.nmTop().resize(true) }", 150);
                    }
                    $('.playerNext, .playerPrev, .playerPages').hide();
                    $('.playerClose').html(t.CLOSE_WINDOW).click( function() {
                        $('.mplayerWrapper .closeFW.oneElement').trigger('click');
                        $(".playerHTML").hide();
                        $.nmTop().close();
                    });
                }
                // -- adding start event
                if(segment_id){
                    ing.callbacks.mp.info_handler(JSON.stringify({'event_type': 'START', 'segment_id': segment_id}));
                }
                return false;
            },
            /**
             * Callback from flash player. Passes currently played
             * item index and handles changing state of an appropriate
             * HTML object.
             */
            activeItem_handler: function(index) {
                this.parent.data.activeItem = index;
                var currentIndex = false;
                var cnf = this.parent.config;

                //Making active module always visible
                var positionOfChar = $(cnf.module).css('left').indexOf("px");
                if ( -($(cnf.module).css('left').slice(0,positionOfChar)) < cnf.elemWrapperWidth * (index-5)+40 ) {
                    $(cnf.module).css('left', -(cnf.elemWrapperWidth * (index-4))+90+'px');
                }
                if ( -($(cnf.module).css('left').slice(0,positionOfChar)) > cnf.elemWrapperWidth * index ) {
                    $(cnf.module).css('left', -(cnf.elemWrapperWidth * index)+'px');
                }

                $(this.parent.config.module).find('li').each( function(i) {
                    if(i == index) {
                        $(this).addClass('current');
												//console.log('new current');
                        currentIndex = index;
                    } else {
                        if($(this).hasClass('current')) {
                            //$(this).addClass('completed');
                        }
                        $(this).removeClass('current');
                    }
                });

                this.saveStateFromPlayer(currentIndex);
            },
            this_is_finished: function() {
               //console.log('finished');
               this.saveStateFromPlayer('last');
            },
            /**
            * Storing currently played segment in a cookie
            * to provide "Continue course" functionality
            */
            saveStateFromPlayer: function(state) {
                this.parent.helpers.cookie.set('ing_last', JSON.stringify({
                    'courseId': app.data.moduleJSON.meta.id,
                    'index': state
                }), this.parent.config.cookieTime);
            }
        }
    },
    /**
     * App's data store
     */
    this.data = {},
    /**
     * App's HTML elements. Every element has
     * it's own template and data store.
     *
     * A simple element uses following fields:
     * - data:    a data store; it's values are used
     *            to parse into a template
     * - tpl:     a html template; used to create DOM node
     * - events:  element's events attached when an element
     *            is being inserted into the DOM. Every event
     *            object should have 2 fields:
     *            - name:     an event name
     *            - handler:  a handler function
     */
    this.elements = {
        parent: this,
        /**
         * Helper function. Parses tag's data
         * and it's template and returns HTML output.
         * Replaces {variable} markup by appropriate
         * value from object's data store.
         * If a value is not found an empty string is returned.
         */
        parse: function(obj) {
            return obj.tpl.replace( /\{[^\}]*\}/g, function(m) {
                return obj.data[m.substr(1, m.length - 2)] || '';
            });
        },
        /**
         * Adds deferred events to an object. The events
         * are attached to the object upon its placing within
         * the DOM structure.
         */
        addDeferredEvents: function(obj, node) {
            if(obj.events) {
                for(var i = 0, len = obj.events.length; i < len; i++) {
                    $('#' +node.attr('id')).live(obj.events[i].name, obj.events[i].handler);
                }
            }
        },
        /**
         * Attaches object to DOM and binds all object's
         * event handlers.
         * @todo: Find a way to attach object's interfaces
         */
        attach: function(obj, root) {
            var node = this.getObj(obj);
            $(root).append(node);
            if(obj.events) {
                for(var i = 0, len = obj.events.length; i < len; i++) {
                    node.bind(obj.events[i].name, obj.events[i].handler);
                }
            }
            return node;
        },
        /**
         * Generates unique id for a HTML object
         */
        generateId: function() {
            do {
                var id = 'id_' + new Date().getTime();
            } while(this.parent.data.map[id]);
            this.parent.data.map[id] = true;
            return id;
        },
        /**
         * Returns a jQuery-style object.
         * @todo: Try to attach all events to this object.
         */
        getObj: function(obj) {
            var ret = $(this.parse(obj));
            ret.attr('id', function(e) {
                return $(this).attr('id') || Ing.findInDOM().elements.generateId();
            });
            this.parent.data.map[ret.attr('id')] = obj.data;
            return ret;
        },
        /**
         * Modal window button
         */
        button: function(details, events) {
            this.data = $.extend(true, {}, details);
            this.events = events;
            //this.tpl = '<a class="button-gray nyroModalClose nyroModalCloseButton" href="#">{text}</a>';
            this.tpl = '<a class="button-gray" href="#">{text}</a>';
        },
        /**
         * Course details badge. Used in a assignment manager
         */
        courseDetails: function(details) {
            this.data = $.extend(true, {}, details);
            this.data.completion_msg = app.helpers.htmlSpecialDecoder(this.data.completion_msg);
            this.events = [];
            if (this.data.type == 70) {
                thumbnailURL = Ing.findInDOM().config.mediaURL + 'img/file_type_scorm.png';
            }
            else {
                thumbnailURL = "{thumbnail_url}";
            }
            this.tpl = '<h3>{title}</h3><dl>' +
            // '<dt>' + t.ID + ':</dt><dd>{id}</dd>' +
            // '<dt>' + t.TITLE + ':</dt><dd>{title}</dd>' +
            '<dt>' + t.AUTHOR + ':</dt><dd>' + this.data.owner + '</dd>' +
            '<dt>' + t.ALLOW_DOWNLOADING + ':</dt><dd>';
            this.tpl += (this.data.allow_download)? t.YES: t.NO;
            this.tpl += ' </dl>' +
            '<dl><dt>' + t.PUBLISHED_DATE + ':</dt><dd>' + app.helpers.timestampToDate(this.data.published_on, true) + '</dd>' +
            '<dt>' + t.ALLOW_SKIPPING + ':</dt><dd>';
            this.tpl += (this.data.allow_skipping)? t.YES: t.NO;
            this.tpl += '</dl>' +
            '<dl><dt>' + t.LANGUAGE + ':</dt><dd>' + this.data.language_name + '</dd></dl>' +
            '</dl><div class="preview"><span>' + t.PREVIEW + '</span></div>' +
            //'</dl><div class="preview" style="background-image: url(\''+ this.data.thumbnail_url+'\'); background-position: center center; background-repeat: no-repeat;"></div>' +
            '<div class="fleft leftText"><h3 class="clear">' + t.COURSE_OBJECTIVE + '</h3><div class="mdetails">{objective}</div>' +
            '<h3 class="clear">' + t.COURSE_MESSAGE + '</h3><div class="mdetails">{completion_msg}</div></div><div class="fleft">';



            var html = '';
            // var temporary_tags = $.parseJSON(data.meta.groups_ids_can_be_assigned_to);
            var groups_ids_can_be_assigned_to = eval(this.data.groups_ids_can_be_assigned_to);
            if(groups_ids_can_be_assigned_to.length > 0) {
            	html += '<div class="assignmentsWrapper"><h3 class="clear">' + t.CAN_BE_ASSIGNED_TO + '</h3><ul class="taglist">';
                var ing = Ing.findInDOM();

                for(var i = 0, len = groups_ids_can_be_assigned_to.length; i < len; i++) {
                	var id = groups_ids_can_be_assigned_to[i];
                    if (id>0) {
                        html += ing.elements.getObj(
                        new ing.elements.tag(ing.data.groups[id].name + ';', false)
                        ).wrap('<div />').parent().html();
                    }
                }
                html += '</ul></div>';
               }
            this.tpl+= html;

            var html = '';
            if(this.data.groups_names && this.data.groups_names.length > 0) {
            	html += '<div class="assignmentsWrapper"><h3 class="clear">' + t.ASSIGNMENTS + '</h3><ul class="taglist">';
                var ing = Ing.findInDOM();

                for(var i = 0, len = this.data.groups_names.length; i < len; i++) {
                    html += ing.elements.getObj(
                    new ing.elements.tag(this.data.groups_names[i] + ';', false)
                    ).wrap('<div />').parent().html();
                }
                html += '</ul></div>';
               }
            this.tpl += html;
            this.tpl += '</div><div class="clear"></div>';	// right column

        },
        /**
         * File details wrapper. Displays file details
         * in an info box.
         */
        details: function(obj, editable) {
            if(editable === undefined){
                editable = true;
            }
            var ing = Ing.findInDOM();
            this.data = $.extend(true, {}, obj);
            if (this.data.note.length > 28) {
            	this.data.short = this.data.note.substr(0,30) + '...';
            } else {
            	this.data.short = this.data.note;
            }
            this.events = [];
            if (this.data.type == 70) {
                thumbnailURL = Ing.findInDOM().config.mediaURL + 'img/file_type_scorm.png';
            }
            else {
                thumbnailURL = "{thumbnail_url}";
            }

            this.tpl = '<h3 class="fileTitle">{title}</h3>';
            this.tpl += '<div><a href="' + ing.config.mediaURL + 'swf/player.swf" class="nm preview" >' +
			            '<span>' + t.PREVIEW + '</span>' +
			            '</a>' +
            			'<span class="propertyTitle" style="line-height: 23px; clear:none">' + t.OWNER + ': </span>';
            if(this.data.tags.length > 0) {
                var ing = Ing.findInDOM();
                var html = '';
                for(var i = 0, len = this.data.tags.length; i < len; i++) {
                	if (this.data.tags[i][1] == "owner"){
	                    html += ing.elements.getObj(
	                    new ing.elements.tag(this.data.tags[i][0], false)
	                    ).wrap('<div />').parent().html();
                	}
                }
                this.tpl += '<ul class="taglist" style="clear:none; margin-top:-4px; margin-right: 8px">' + html + '</ul>';
            }
            this.tpl += '<dl>' +
            // '<dt>' + t.OWNER + ':</dt><dd class="highlight">{owner}</dd>' +
            '<dt>' + t.DURATION + ':</dt><dd> ' + obj.duration  + " " + t.MINUTES + '</dd>' +
            '<dt>' + t.ADDED + ':</dt><dd>{created_on}</dd>';

            if(this.data.expires_on == null)
            	this.tpl = this.tpl + '<dt>' + t.EXPIRATION_DATE + ':</dt><dd>'+ t.DATE_NOT_SET + '</dd></dl>';
        	else
            	this.tpl = this.tpl + '<dt>' + t.EXPIRATION_DATE + ':</dt><dd>{expires_on}</dd></dl>';

            this.tpl = this.tpl + '<dl><dt>' + t.LANGUAGE + ':</dt><dd>{language}</dd>' +
                    '<dt>' + t.DOWNLOADABLE + ':</dt><dd>{allow_downloading}</dd>' +
            '<dt class="hidden">' + t.ID + ':</dt><dd class="hidden" id="' + ing.config.fileId.substr(1) + '">{id}</dd>' +
            '</dl>' +
            '<div><span class="propertyTitle">' + t.NOTE + '</span>:<br /><a href="#" class="contentNote">' +
        	'{short}' +
        	'</a><div class="tooltip">{note}</div></div>' +
            '<dl class="wide">' +
            '<dt>' + t.CURRENT_USAGE + ':</dt><dd>{usage} ' + t.MODULES + ' ({usage_active} '+ t.ACTIVE + ')</dd>' +
            // '<dt>' + t.ALLOW_DOWNLOADING + ':</dt><dd>{allow_downloading}</dd>' +
            // '<dt>' + t.ALLOW_SCALING + ':</dt><dd>{allow_scaling}</dd>' +
            // '<dt>' + t.GROUPS + ':</dt><dd>{groups}</dd>' +
            '</dl><div class="hr"></div>';
            this.tpl += '<div><span class="propertyTitle">' + t.GROUPS + ': </span>';
            if(this.data.tags.length > 0) {
                var ing = Ing.findInDOM();
                var html = '';
                for(var i = 0, len = this.data.tags.length; i < len; i++) {
                	if (this.data.tags[i][1] == 'group'){
	                    html += ing.elements.getObj(
	                    new ing.elements.tag(this.data.tags[i][0], false)
	                    ).wrap('<div />').parent().html();
                	}
                }
                this.tpl += '<ul class="taglist">' + html + '</ul>';
            }
            this.tpl += '</div><div><span class="propertyTitle">' + t.TAGS + ': </span>{tags}';
            if(this.data.tags.length > 0) {
                var ing = Ing.findInDOM();
                var html = '';
                for(var i = 0, len = this.data.tags.length; i < len; i++) {
                	if (this.data.tags[i][1] == 'custom'){
	                    html += ing.elements.getObj(
	                    new ing.elements.tag(this.data.tags[i][0], false)
	                    ).wrap('<div />').parent().html();
                	}
                }
                this.data.tags = '<ul class="taglist">' + html + '</ul>';
            }
            if(this.data.groups.length > 0) {
                this.data.groups = '<span class="highlight">' +
                this.data.groups.join('</span>, <span class="highlight">') +
                '</span>';
            }
            this.tpl += '</div>';
            if(editable && this.data.is_editable){
                this.tpl += '<div class="hr"></div><a class="button-normal button-big-no-width" href="{id}">' + t.EDIT + '</a>';
                if(this.data.is_removable){
                    this.tpl += '<a id="removeFile" class="button-normal button-big-no-width" href="{id}/delete/">' +
                    '<img class="icoRemove icon" alt="" src="/media/img/blank.gif">' + t.REMOVE + '</a>';
                }
            }
            this.data.created_on = ing.helpers.timestampToDate(this.data.created_on);
            if(this.data.expires_on) {
                this.data.expires_on = ing.helpers.timestampToDate(this.data.expires_on);
            }
            this.data.type = ing.data.filetypes[this.data.type];
        },

        /**
         * Module dot used for displaying assignments.
         */
        dotLarge: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<span class="movableDot dot">' +
            '<span class="progress0" title="{title}"> </span>' +
            '{short_title}</span>';
        },
        /**
         * Single file item. Displayed in a roller.
         * @todo: Add item's interfaces here.
         */
        fileItem: function(details, i) {
            this.data = $.extend(true, {}, details);
            this.data.title_escaped = this.data.title.replace(/&lt;/gi, '<');
            this.data.title_escaped = this.data.title_escaped.replace(/&gt;/gi, '>');
            this.data.title_escaped = this.data.title_escaped.replace(/<\/?[^>]+>/gi, '');
            this.events = [];
            this.tpl = '<li title="{title_escaped}"{className}>' +
            '<a id="file_' + i + '" href="#" class="singleFile"><div class="activeWrapper"><img src="' +
            Ing.findInDOM().config.mediaURL + 'img/blank.gif"' +
            ' alt=""  class="fileTypeIco ' +
            Ing.findInDOM().data.fileicons[this.data.type] + '" /></div>{title}</a></li>';
        },
        /**
         * Simple group item. Used in a group manager
         */
        groupItem: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<option value="{id}">{name}</option>';
        },
        /**
         * Simple group row. Used in content assignment.
         */
        groupRow: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<li{className}>' +
            '<span class="groupName" title="{name}">{name}</span>' +
            '<a class="prev browse fleft"><img src="' + Ing.findInDOM().config.mediaURL + 'img/blank.gif"' + ' alt="" /></a>' +
            '<div id="dots_{id}Wrapper" class="dotsWrapper"><span id="dots_{id}" class="dots">&nbsp;</span></div>' +
            '<a class="next browse fright"><img src="' + Ing.findInDOM().config.mediaURL + 'img/blank.gif"' + ' alt="" /></a>' +
            '</li>';
        },
        /**
         * Basic list template. Used for creating filelist
         * within the roller.
         */
        list: function() {
            this.data = {};
            this.events = [];
            this.tpl = '<ul></ul>';
        },
        /**
         * Basic list element.
         */
        listElement: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<li>{content}</li>';
        },
        /**
         * Module row used in module manager.
         */
        moduleManagerRow: function(details) {
            // classes: first, last, odd, even
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<li class="{className}">' +
            '<span class="moduleName" ownerid="{ownerId}">{title}</span>' +
            '<span class="moduleAssigned">{assignments}</span>' +
            '<span class="moduleStatus"><img class="ico_{status}" src="' +
            Ing.findInDOM().config.mediaURL + 'img/blank.gif" alt="" /></span>' +
            '</li>';
        },
        /**
         * Simple module row. Used in content assignment.
         */
        moduleRow: function(details) {
        	var ing = Ing.findInDOM();
            this.data = $.extend(true, {}, details);
            this.events = [];
            if (this.data.owner.length > 25)
            	this.data.shortText = this.data.owner.substr(0, 23) + "...";
            else
            	this.data.shortText = this.data.owner;
            this.tpl = '<li {className}><a href="#"></a>' +
            '<span class="moduleCheck"><input type="checkbox" /></span>'+
            '<span class="moduleName" lang="{language}">{title}</span>'+
            '<span class="moduleAuthor" ownerid="{ownerId}" title="{owner}">{shortText}</span>'+
            '<div class="modulePreview"><a href="#" class="previewBtn">' + t.PREVIEW + '</a></div>';

            var groups_ids_can_be_assigned_to = $.parseJSON(this.data.groups_ids_can_be_assigned_to);
            this.tpl+= '<input type="hidden" class="groups" value="'+ this.data.groups_ids_can_be_assigned_to +'" />';
            this.tpl+= '<input type="hidden" class="ownerid" value="{ownerId}" />';
            this.tpl+= '</li>';


        },
        /**
         * HTML player for content, that cannot be displayed in standard
         * Flash Player.
         *
         * Notice: The outer div element is used as a wrapper
         * for nyroModal library.
         */
        playerHTML: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div><div class="playerHTML"><a href="#" class="playerClose icoClose">&nbsp;</a>' +
            '<a href="#" class="playerPrev goBack" title="' + t.PAGE_PREV + '">&nbsp;</a>' +
            '<a href="#" class="playerNext goAhead" title="' + t.PAGE_NEXT + '">&nbsp;</a>' +
            '<iframe src="{src}"></iframe><div class="hr"></div>' +
            '<a href="#" class="playerPrev" title="' + t.PAGE_PREV + '">&nbsp;</a>' +
            '<a href="#" class="playerNext" title="' + t.PAGE_NEXT + '">&nbsp;</a>' +
            '<span class="playerPages">&nbsp;</span>' +
            '<a href="#" class="playerClose">&nbsp;</a>' +
            '</div></div>';
        },
        /**
         * SCORM Player window
         */
        playerSCORM: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div><div class="playerSCORM"><a href="#" class="playerClose icoClose">&nbsp;</a>' +
            '<iframe name="scormFrame" id="scormFrame" src="{src}"></iframe>' +
            '<div class="hr"></div>' +
            '<a href="#" class="playerClose">&nbsp;</a></div></div>';
        },
        /**
         * Embeded html and scorm player. Used when app is in html5 mode
         */
        playerHTML5: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div class="playerHTML"><div class="playerHTML5">' +
            '<iframe src="{src}"></iframe></div>' +
            '<div class="playerBottomLabel">' +
            '<label class="nameLabel">{title}</label>' +
            '<span class="playerPages">&nbsp;</span>' +
            '<div class="setFullscreen"></div>' +
            '<a href="#" class="skipTo hidden">' + t.CLICK_TO_SKIP + '</a>' +
            '</div></div>';
        },
        /**
         * Report details badge
         */
        reportDetails: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<h3>{name}</h3><dl>' +
            '<dt>' + t.ADDED + ':</dt><dd>{created_on}</dd>' +
            '<dt>' + t.LAST_MODIFIED + ':</dt><dd>{modified_on}</dd>' +
            '<dt>' + t.LAST_EXECUTED + ':</dt><dd>{executed_on}</dd>' +
            //'<dt>' + t.TEMPLATE + ':</dt><dd>{template_path} ' +
            //'<a href="{template_url}" class="button-gray">' + t.DOWNLOAD + '</a></dd>' +
            '<dt>' + t.EXECUTION + ':</dt><dd>{schedule_type}{schedule_day}</dd>' +
            '<dt>' + t.NOTE + ':</dt><dd>{note}</dd>' +
            '</dl>';
            if(this.data.schedule_day == 0) {
                this.data.schedule_day = '';
            } else {
                this.data.schedule_day = ', ' + t.EVERY + ' ' + this.data.schedule_day;
            }
        },
         /**
         * Imported report details badge
         */
        importedReportDetails: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<h3>{name}</h3><dl>' +
            '<dt>' + t.ADDED + ':</dt><dd>{created_on}</dd>' +
            '<dt>' + t.AUTHOR + ':</dt><dd>{author}</dd>' +
            '<dt>' + t.LAST_MODIFIED + ':</dt><dd>{modified_on}</dd>' +
            '<dt>' + t.USER_SHOWN + ':</dt><dd>' + (details['user_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.USER_REQUIRED + ':</dt><dd>' + (details['user_required'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.GROUP_SHOWN + ':</dt><dd>' + (details['group_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.GROUP_REQUIRED + ':</dt><dd>' + (details['group_required'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.COURSE_VISIBLE + ':</dt><dd>' + (details['course_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.COURSE_REQUIRED + ':</dt><dd>' + (details['course_required'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.ADMIN_SHOWN + ':</dt><dd>' + (details['admin_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.ADMIN_REQUIRED + ':</dt><dd>' + (details['admin_required'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.DATE_FROM_SHOWN + ':</dt><dd>' + (details['date_from_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.DATE_TO_SHOWN + ':</dt><dd>' + (details['date_to_shown'] ? t.YES : t.NO) + '</dd>' +
            '<dt>' + t.TEMPLATE + ':</dt><dd>{template_path} ' +
            '<a href="{template_url}" class="button-gray">' + t.DOWNLOAD + '</a></dd>' +
            '<dt>' + t.NOTE + ':</dt><dd>{note}</dd>' +
            '</dl>';
        },
        /**
         * Report result file
         */
        reportFileRow: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            if(this.data.status == '0') {
                this.tpl = '<li class="{className}">' +
                '<span class="reportFile">{result_path}</span>' +
                '<span class="reportDownload"><a href="{result_url}">' + t.DOWNLOAD_PDF + '</a></span>' +
                '<span class="reportDownload"><a href="{csv_result_url}">' + t.DOWNLOAD_CSV + '</a></span>' +
                '<span class="reportDownload"><a href="{html_result_url}" target="_blank">' + t.DOWNLOAD_HTML + '</a></span>' +
                '</li>'
            } else {
                this.tpl = '<li class="{className}">' +
                '<span class="reportFile">' + t.REPORT_GEN_FAILED + '</span>' +
                '<span class="reportDownload"></span>' +
                '</li>'
            }

        },
        /**
         * Report list item
         */
        reportRow: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [{
                name: 'click',
                handler: function(e) {
                    var ing = Ing.findInDOM();
                    ing.triggerEvent('reportChanged', [this]);
                    return false;
                }
            }];

            this.tpl = '<li class="{className}">';
            var reportName = this.data.name;
            if (reportName.length > 25) {
            	this.data.shortText = reportName.substr(0,22)+"...";
            	this.tpl += '<span class="reportName" ownerid="{owner_id}">{shortText}</span>';
            }
            else
            	this.tpl += '<span class="reportName" ownerid="{owner_id}">{name}</span>';
            this.tpl += '<span class="reportCron">{cronIcon}</span>' +
            '<span class="reportTime">{executed_on}</span>' +
            '</li>';
            if(this.data.schedule_type_raw != 0){
                this.data.cronIcon = '<img class="cronIcon" src="' +
                        Ing.findInDOM().config.mediaURL + 'img/blank.gif" alt="" />';
            }
        },
         /**
         * Report template list item
         */
        reportTemplateRow: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [{
                name: 'click',
                handler: function(e) {
                    var ing = Ing.findInDOM();
                    ing.triggerEvent('reportChanged', [this]);
                    return false;
                }
            }];
            this.tpl = '<li class="{className}">';
            var reportName = this.data.name;
            if (reportName.length > 25) {
            	this.data.shortText = reportName.substr(0,22)+"...";
            	this.tpl += '<span class="reportName">{shortText}</span>';
            }
            else
            	this.tpl += '<span class="reportName">{name}</span>';
            this.tpl += '<span class="reportAuthor">{author}</span>' +
            '</li>';
            if(this.data.schedule_type_raw != 0){
                this.data.cronIcon = '<img class="cronIcon" src="' +
                        Ing.findInDOM().config.mediaURL + 'img/blank.gif" alt="" />';
            }
        },
        /**
         * A segment used within shelfs and modules.
         *
         */
        segment: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<li title="{title}" class="ui-draggable">' +
            '<a href="#" class="singleFile"><img src="' +
            Ing.findInDOM().config.mediaURL + 'img/blank.gif"' +
            ' alt=""  class="fileTypeIco ' +
            Ing.findInDOM().data.fileicons[this.data.type] + '" />{title}</a></li>';
        },
        /**
         * Throbber element. Indicates asynchronous background action.
         * Should be attached to affected element.
         */
        throbber: function(id) {
            this.data = {};
            this.events = [];
            this.tpl = '<div class="throbber" id="throbber_' + id + '">' +
            '<img class="throbber_img" src="' + Ing.findInDOM().config.mediaURL + 'img/throbber.gif" /></div>';
        },
        /**
         * Throbber element. Indicates asynchronous background action.
         * Should be attached to affected element.
         */
        opaque_throbber: function(id) {
            this.data = {};
            this.events = [];
            this.tpl = '<div class="opaque_throbber" id="throbber_' + id + '"></div>';
        },
        /**
         * A plain segment used with a module viewer.
         *
         */
        plainSegment: function(details) {
        	var ing = Ing.findInDOM();
            this.data = $.extend(true, {}, details);

            if(typeof(ing.data.first_num)=="undefined")
            	ing.data.first_num = 1;

            if ((this.data.start == 1) && (ing.data.first_num == 1))
        		ing.data.first_to_learn = true;

            if (this.data.start == 0) {
            	ing.data.first_to_learn = true;
            	ing.data.first_num = 0;
            }

    		// this.data.allow_skipping = false; // MOCK

            this.events = [];
            this.data.separator1 = this.data.duration == '' ? '' : '<br />';
            this.data.separator2 = this.data.duration == '' ? '' : ' - ';
            this.tpl = '<li title="{title}"';
            if(this.data.is_learnt) {
                this.tpl += ' class="completed"';
            }
            this.tpl += '>' +
            '<a href="#" class="singleFile" title="{title}{separator2}{duration} min"><img src="' +
            Ing.findInDOM().config.mediaURL + 'img/blank.gif"' +
            ' alt=""  class="fileTypeIco ' +
            //Ing.findInDOM().data.fileicons[this.data.type] + '" /></a>{title}{separator1}{duration} min';
            Ing.findInDOM().data.fileicons[this.data.type] + '" /></a>{title}';
            if(this.data.allow_downloading == true && this.data.is_learnt){
                this.tpl += ' <button class="segmentDownload" onclick="window.location.href=\'{download_url}\'" title="' + t.SEGMENT_DOWNLOAD + '"></button>';
            }
            if (!this.data.is_learnt && !this.data.allow_skipping && !ing.data.first_to_learn)
            	this.tpl += '<div class="courseApla"></div>'
            this.tpl += '</li>';
            if (ing.data.first_to_learn) ing.data.first_to_learn = false;
            if(this.data.is_learnt) {
                ing.data.first_to_learn = true;
            }


        },
        /**
         * Sound background element
         *
         */
        sound: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div class="active"><a href="#" title="{title}">' +
            /*'<img class="note" src="' +
             Ing.findInDOM().config.mediaURL + 'img/blank.gif" alt="" />*/'<span>snd</span>' +
            '<a href="#" class="remove_snd">(' + t.REMOVE.toLowerCase() + ')</a>' +
            '<a class="sndMode';
            if(this.data.playback_mode == 'once'){
                this.tpl += ' no-repeat';
            }else{
                this.tpl += ' repeat';
            }
            this.tpl += '" href="#"></a></a>' +
            '</div>';
        },
        /**
         * Plain sound background used with a module viewer.
         */
        plainSound: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div><span title="{title}">snd</span></div>';
        },
        /**
         * Tag element used on a taglist.
         */
        tag: function(tagName, cancellable) {
            this.data = {};
            this.data.name = tagName;
            this.data.cancellable = typeof cancellable == 'undefined' ? true : false;

            this.events = [];
            this.tpl = '<li>{name}';
            if(this.data.cancellable) {
                this.tpl += '<a href="#" title="' + t.REMOVE_FROM_TAGLIST + '">' +
                '<img class="delete" src="' +
                Ing.findInDOM().config.mediaURL + 'img/blank.gif" alt="" /></a>';
            }
            this.tpl += '</li>';
            this.events.push({
                name: 'click',
                handler: function(e) {
                    if($(e.target).is('img')) {
                        Ing.findInDOM().triggerEvent('tagRemoved', [$.trim($(this).text().replace('x ', ''))]);
                        $(this).remove();
                    }
                    return false;
                }
            });

        },
        /**
         * User details badge. Used in a group manager
         */
        userDetails: function(details, allowEdit) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<table>';

            this.tpl += '<tr><th>' + t.ROLE + ':</th><td style="text-transform: capitalize;">{user_type_translated}</td></tr>' +
            '<tr><th>' + t.USERNAME + ':</th><td><span>{username}</span></td></tr>' +
            '<tr><th>' + t.FIRST_NAME + ':</th><td>{first_name}</td></tr>' +
            '<tr><th>' + t.LAST_NAME + ':</th><td>{last_name}</td></tr>' +
            '<tr><th>' + t.EMAIL + ':</th><td>{email}</td></tr>' +
            '<tr><th>' + t.PHONE + ':</th><td>{phone}</td></tr>' +
            '<tr><th>' + t.GROUPS + ':</th><td class="myGroupList">{assignments}</td></tr>';
            if ($('#userlist:focus').length > 0) {
	            //if(this.data.user_type!='user') {
                    if(this.data.user_type!='OCL recipient' && this.data.user_type!='recipient') {
	                this.tpl += '<tr><th>' + t.MANAGES + ':</th><td class="myGroupList">{managements}</td></tr>';
	            }
              //console.log(this.data);
	           // if(this.data.user_type!='user') {
                    if(this.data.user_type!='OCL recipient' && this.data.user_type!='recipient') { 
	                if(this.data.manages.inArray($('#my_groups').val())) {
	                    this.tpl += '<tr><th> &nbsp; </th><td><a class="button-normal" href="#" id="tm">{% trans "Remove" %}' + t.MANAGER_REMOVE + '</a></td></tr>';
	                } else {
	                    this.tpl += '<tr><th> &nbsp; </th><td><a class="button-normal" href="#" id="tm">' + t.MANAGER_ADD + '</a></td></tr>';
	                }

	            }
            }
            this.tpl += '<tr><td colspan=2>{status_text}</td></tr>' +
            '</table>';
            if(!(this.data.is_active)) {
                this.data.status_text = '<strong>' + t.USER_INACTIVE + '</strong>';
            }
            if(allowEdit == undefined) {
                allowEdit = false;
            }
            var ssuper = Ing.findInDOM().data.ssuper;
            var my_id = Ing.findInDOM().data.my_id;
            if(allowEdit == true) {
                this.tpl += '<div class="hr"></div><div>';
                if(this.data.id != my_id) {
                    if(this.data.ldap_user!='*' && (ssuper==true || (ssuper==false && this.data.user_type.indexOf('recipient')!=-1))) {
                        this.tpl += '<a class="button-normal" href="#" id="eu">' + t.USER_EDIT + '</a>';
                        if(ssuper || !this.data.has_tracking) {
                            this.tpl += '<a class="button-normal" href="#" id="ru"><img class="icoRemove icon" src="/media/img/blank.gif" alt="">{% trans "Remove" %}' + t.USER_REMOVE + '</a>';
                        }
                    }
                    if(this.data.is_active && this.data.activation_allowed) {
                        this.tpl += '<a class="button-normal" href="#" id="du">' + t.USER_DEACTIVATE + '</a>';
                    } else {
                        if(this.data.activation_allowed) {
                            this.tpl += '<a class="button-normal" href="#" id="au">' + t.USER_ACTIVATE + '</a>';
                        }
                    }
                } else {
                    this.tpl += '<a class="button-normal" href="#" id="eu">' + t.USER_EDIT + '</a>';
                }


                this.tpl += '</div>'
            }
            if(!this.data.phone) {
                this.data.phone = '&nbsp;';
            }

        },
        /**
         * Simple user item. Used in a group manager
         */
        userItem: function(details) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<option value="{id}" class="{user_type}">{last_name} {first_name}{ldap_user}{plus_user} {status_text}</option>';
            if(!(this.data.is_active)) {
                this.data.status_text = ' (' + t.INACTIVE.toLowerCase() + ')';
            }
        },
        /**
         * Window object.
         * Window object can contain one or more buttons passed as
         * an array as a second constructor argument.
         *
         * Each button should have following structure:
         * {
         * 	text: 'A string containing button text',
         * 	events: [{
         * 		name: 'Name of the event',
         * 		handler: function(e){} - function handling given event
         * 	}]
         * }
         *
         * A button can have more than one event assigned (e.g. click
         * event, mouseover, mouseout or any custom event).
         *
         * WARNING: by default no event is assigned, so in order of any button
         * to work, it should have at least a click event handler defined.
         *
         * By default, each window has a closing button, which can be disabled.
         */
        window: function(details, buttons, hideClosingButton, afterCloseAction) {
            this.data = $.extend(true, {}, details);
            this.events = [];
            this.tpl = '<div class="modalWrapper hidden">' + // user only due to the nyroModal issues
            '<div class="modalContent modalWindow"{style}>' +
            '<h1>{title}</h1><a class="close nyroModalClose nyroModalCloseButton" href="#"></a>' +
            '<div class="separator"></div>' +
            '<div class="windowMessage">{msg}</div>' +
            '<div class="windowButtons">{buttons}</div>' +
            '<div class="hr"></div>' +
            '</div>' +
            '</div>';
            this.data.buttons = '';
            var ing = Ing.findInDOM();
            var els = ing.elements;
            if(hideClosingButton === undefined || hideClosingButton === null) {
                hideClosingButton = false;
            }
            if(buttons === undefined || buttons === null) {
                buttons = [];
            }
            if(afterCloseAction === undefined) {
                afterCloseAction = function() {}
            }
            // generating default closing button
            if(buttons.length == 0 && !hideClosingButton) {
                buttons = [{
                    text: 'OK',
                    events: [{
                        name: 'click',
                        handler: function(e) {
                            $.nmTop().close();
                            afterCloseAction();
                            return false;
                        }
                    }]
                }]
            }
            if(buttons.length > 0) {
                for(var i = 0, len = buttons.length; i < len; i++) {
                    var btnObj = new els.button({text: buttons[i].text}, buttons[i].events);
                    var btn = els.getObj(btnObj);
                    this.data.buttons += btn.wrap('<div></div>').parent().html();
                    els.addDeferredEvents(btnObj, btn);
                }
            }
        }
    },
    /**
     * Group manager.
     */
    this.gm = {
        parent: this,
        /**
         * Loads users, groups and their assignments into a data store.
         */
        loadData: function(allowUserEdit, loadIntoMyGroups) {
            $.get('/management/users/list/', function(data) {
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                var ing = Ing.findInDOM();
                var dat = ing.data;
                dat.groups = data.groups;
                dat.users = data.users;
                dat.memberships = data.memberships;
                dat.mygroups = data.mygroups;
                dat.groupless = data.groupless;
                dat.ssuper = data.ssuper;
                dat.my_id = data.my_id;
                dat.memberships['-1'] = [];
                dat.gid = 0;
                $.each(dat.users, function(key, value) {
                    dat.memberships['-1'].push(value.id);
                });
                dat.memberships['-2'] = [];
                dat.gid = 0;
                $.each(dat.groupless, function(key, value) {
                    dat.memberships['-2'].push(value);
                });
                ing.gm.loadGroups();
                if (loadIntoMyGroups) {
                    ing.gm.loadMyGroups(true);
                    ing.gm.loadGroupsIntoMyGroups();
                }
                else {
                    ing.gm.loadMyGroups();
                }
                if(typeof ing.data.savedState == 'object') {
                    ing.gm.restoreState();
                    app.triggerEvent('groupListChange', 'groups');
                    app.triggerEvent('groupListChange', 'my_groups');
                    if(Ing.findInDOM().data.activeUser) {
                        if(allowUserEdit == undefined) {
                            allowUserEdit = false;
                        }
                        Ing.findInDOM().gm.refreshUserDetails(Ing.findInDOM().data.activeUser.id, allowUserEdit);
                    }
                    $("#my_groups, #groups").sb('refresh');
                }

            });
        },
        /**
         * Loads groups from a local data store and creates
         * selectable list of groups.
         */
        loadGroups: function() {
        	var ing = Ing.findInDOM();
            var groups = ing.gm.sortGroups(this.parent.data.groups);
            var elems = {
                '0' : {id: '0', name: ' --- '},
                '-1': {id: -1, name: t.ALL_USERS},
                '-2': {id: -2, name: t.NO_GROUP}
            }
            var tmp = $.extend(elems, groups);
            $('#groups').html('');
            $.each(tmp, function(key, value) {
                var g = new ing.elements.groupItem(value);
                ing.elements.attach(g, $('#groups'));

                if($('#my_groups_tmp') && key != '-1' && key != '-2') {
                   ing.elements.attach(g, $('#my_groups_tmp'));
                }
            });
            $("#groups").sb('refresh');
            $('#self_register_group_list').html('');
            $('#all_group_list').html('');
            $.each(groups, function(key, value) {
                var g = new ing.elements.groupItem(value);
                
                if (value.self_register_enabled) {
                    ing.elements.attach(g, $('#self_register_group_list'));
                } else {
                    ing.elements.attach(g, $('#all_group_list'));
                }
            });

        },
        /**
         * Loads user's groups from a local data store
         * and creates selectable list of groups.
         */
        loadMyGroups: function(loadIntoMyGroups) {
        	var ing = Ing.findInDOM();
        	var groups = ing.gm.sortGroups(this.parent.data.mygroups);
            var elems = {
                '0' : {id: '0', name: ' --- '}
            }
            var tmp = $.extend(elems, groups);
            
            $('#my_groups').html('');
            $.each(tmp, function(key, value) {
                var g = new ing.elements.groupItem(value);
                ing.elements.attach(g, $('#my_groups'));
            });
            if (loadIntoMyGroups) {
                $('#my_groups_tmp').html( $("#my_groups").html() );
            }
            $("#my_groups").sb('refresh');
        },
        /**
         * Loads groups from a local data store
         * into #my_groups and creates selectable list of groups.
         */
        loadGroupsIntoMyGroups: function() {
        	var ing = Ing.findInDOM();
            var groups = ing.gm.sortGroups(this.parent.data.groups);
            var elems = {
                '0' : {id: '0', name: ' --- '}
            }
            var tmp = $.extend(elems, groups);
            $('#my_groups').html('');
            $.each(tmp, function(key, value) {
                var g = new ing.elements.groupItem(value);
                ing.elements.attach(g, $('#my_groups'));
            });
            $("#my_groups").sb('refresh');
        },
        /**
         * Return object with sorted groups
         */
        sortGroups: function(arrObj) {
        	var arr = new Array();
        	var retObj = {};
        	
        	$.each(arrObj, function(index, value) {
        		arr.push(value);
        	});
        	//arr.objSort("name");
            arr.sort(function(a, b){
                if (a['name'].toLowerCase()>b['name'].toLowerCase()) {
                    return 1;
                } else if (a['name'].toLowerCase()==b['name'].toLowerCase()) {
                    return 0;
                } else {
                    return -1;
                }
            });
        	
        	$.each(arr, function(index, value) {
        		retObj[index + 1] = value;
        	});
        	
        	return retObj;
        },
        /**
         * Restores saved UI state.
         */
        restoreState: function() {
            var saved = this.parent.data.savedState;
            $('#groups').val(saved.groups);
            $('#my_groups').val(saved.my_groups);
            saved = false;
        },
        /**
         * Saves UI state to restore it after
         * a certain refreshing operation finishes.
         */
        saveState: function(obj) {
            if(obj) {
                this.parent.data.savedState = obj;
            } else {
                this.parent.data.savedState = {
                    'groups': $('#groups').val(),
                    'my_groups': $('#my_groups').val()
                }
            }
        },
        /**
         * Creating and refreshing user's details bagde.
         * Badge contains user's details and all assignments
         * of a given user to it's groups.
         */
        refreshUserDetails: function(id, allowEdit) {
            if(allowEdit == undefined) {
                allowEdit = false;
            }
            if(id && this.parent.data.users[id]) {
                var ing = this.parent;
                var list = [];
                $.each(ing.data.memberships, function(key, value) {
                    if(key != -1 && key != -2) {
                        if(value.inArray(id)) {
                            list.push('<span>' + ing.data.groups[key].name + '</span>');
                        }
                    }
                });
                var list_manage = [];
                $.each(ing.data.users[id].manages, function(key, value) {
                    if(ing.data.groups[value] != undefined) {
                        list_manage.push('<span>' + ing.data.groups[value].name + '</span>');
                    }
                });
                var details = ing.data.users[id];
                details.assignments = list.join(', ');
                details.managements = list_manage.join(', ');
                $('#u_details_content').html('');
                $('#u_details_content').append(
                ing.elements.getObj(
                new ing.elements.userDetails(details, allowEdit)
                )
                );
                ing.data.activeUser = {id: id, username: details.username};
            }
        }
    },
    /**
     * Module assignments
     */
    this.ma = {
        parent: this,
        /**
         * Creates HTML object from a group object and attaches
         * all necessary events and interfaces.
         */
        createGroup: function(groupId, className) {
        	var shortTitleLength = 7;
            var app = this.parent;
            var det = app.data.groups[groupId];
            det.className = ' class="' + className + '"';
            var g = app.elements.getObj(new app.elements.groupRow(det));
            $.each(app.data.loadedAssignments[groupId], function(key, value) {
                var dot = app.elements.getObj(new app.elements.dotLarge(value));
                g.find('.dots').append(dot);
            });
            $.each(app.data.loadedAssignments[groupId], function(key, value) {
                if(typeof app.data.assignments[groupId] !== 'object') {
                    app.data.assignments[groupId] = {};
                }
                app.data.assignments[groupId][key] = true;
            });
            g.find('.dots').droppable({
                accept: '#moduleDetailsWrapper .movableDot',
                drop: function(event, ui) {
                    var ing = Ing.findInDOM();
                    var asg = ing.data.assignments;
                    var map = ing.data.map;
                    var grp = map[$(this).parents('li').attr('id')].id;
                    var mod = map[$(ui.draggable).parent().parent().children().first().attr('id')].id;
                    if(typeof asg[grp] !== 'object') {
                        asg[grp] = {};
                    }

                    if($.inArray(grp, $.parseJSON(app.data.modules[mod].meta.groups_ids_can_be_assigned_to)) == -1) {
                        app.helpers.window(t.SYSTEM_MESSAGE, t.CANNOT_ADD_COURSE_TO_THIS_GROUP);
                        return;
                    }

                    if(asg[grp][mod] !== true && app.data.modules[mod]) {
                        asg[grp][mod] = true;
                        var meta = app.data.modules[mod].meta.title;
                        app.data.modules[mod].meta.short_title = meta.substr(0,shortTitleLength)+"...";
                        var tmp = app.elements.getObj(new app.elements.dotLarge(app.data.modules[mod].meta));
                        //var tmp = $(ui.draggable).clone().draggable({appendTo: 'body', helper: 'clone'});
                        $(this).prepend(tmp);
                        if(g.find('.dot').length > 7) {
                            $(this).css('width', parseInt($(this).css('width')) + 76);
                        }
                        var bgCol = $(this).parents('li').css('backgroundColor');
                        tmp.animate({
                            backgroundColor: '#ccc'
                        }, 100).animate({
                            backgroundColor: bgCol
                        }, 1000);
                        ing.data.changed=true;
                    }
                	$('.rollerItems').each(function() {
										var width = $(this).width();
										var container = $(this).parent();
										var container_width = $(container).width();
										if (width < container_width) {
											$(container).siblings(".prev, .next").find('.browse').hide();
										}
									});
                }
            });
            g.find('.dots').css('width', Math.max(g.find('.dot').length, 7)* 76);
            $('#group_list').append(g);
            // -- scrolling events
            $('.next, .prev')
            .unbind('mousedown')
            .unbind('mouseup')
            .mousedown( function() {
                var dir = $(this).hasClass('next') ? 'right' : 'left';
                var id = '#' + $(this).siblings('.dotsWrapper').children('span').attr('id');
                var app = Ing.findInDOM();
                t2 = setInterval( function() {
                    app.helpers.move(dir, app.config.other.movingStep, id);
                }, app.config.other.movingInterval);
            }).mouseup( function() {
                if(t2) {
                    clearTimeout(t2);
                }
            });
            $('#groups option[value=' + groupId + ']').attr('disabled', 'disabled');
            $('#my_groups option[value=' + groupId + ']').attr('disabled', 'disabled');
            $("#groups").sb('refresh');
        },
        /**
         * Loading all requested groups and displaying them
         * in a selectable list.
         */
        loadGroups: function() {
            Ing.findInDOM().helpers.throbber($('#groupsWrapper'));
            $.get(
            '/management/groups/list/?my=0', function(data) {
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                var ing = Ing.findInDOM();
                ing.data.groups = data;

                if($('#my_groups').length) {
                    var tmp = $.extend({'-1': { id: -1, name: t.ALL_GROUPS}}, data);
                    $.each(tmp, function(key, value) {
                        var g = new ing.elements.groupItem(value);
                        ing.elements.attach(g, $('#my_groups'));
                    });
                }
                $.get('/management/groups/list/?my=1', function(data) {
                    if(typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }

                    var tmp = $.extend({'-1': { id: -1, name: t.ALL_GROUPS}}, data);
                    $.each(tmp, function(key, value) {
                        var g = new ing.elements.groupItem(value);
                        ing.elements.attach(g, $('#groups'));
                    });

                    $("#groups").sb('refresh');
                });

                $.get('/assignments/group/modules/', function(data) {
                    if(typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }
                    Ing.findInDOM().data.loadedAssignments = data;
                });


                Ing.findInDOM().helpers.throbber($('#groupsWrapper'), 'remove');
            });
        },
        loadActiveModules: function(moduleId) {
        	if (moduleId == "") {
        		window.location.hash = "myModules";
        		moduleId = "myModules";
        	}

        	var loadModule = parseInt(moduleId);
        	if(loadModule == moduleId-0) {
        		moduleId = "myModules";
        		this._loadModules(moduleId, '/content/modules/active/list/?my=1', loadModule);
        	} else {
        		if (moduleId == "myModules")
	            	this._loadModules(moduleId, '/content/modules/active/list/?my=1', false);
	    		else if (moduleId == 'allModules')
	            	this._loadModules(moduleId, '/content/modules/active/list/?my=0', false);
	        }
        },
        loadModules: function(moduleId) {
             this._loadModules(moduleId, '/content/modules/list/', false);
        },
        /**
         * Loading requested modules, and creating appropriate
         * HTML objects from received JSON objects.
         *
         * @param: moduleId - id of a module that needs
         *         to be activated upon loading
         */
        _loadModules: function(moduleId, url, loadModule) {
        	$("." + moduleId).removeClass("hidden");
            Ing.findInDOM().helpers.opaque_throbber($('.' + moduleId));

            var active = false;
            $.get(url, function(data) {;
            	var active;
            	
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                var ing = Ing.findInDOM();
                ing.data.modules = {}
                $.each(data, function(index, value) {
                    value.meta.className = ' class="' + (index == 0 ? 'first ' : '') + (index%2 ? 'odd' : 'even') + '"';
                    // value.meta.author = t.AUTHOR_UNKNOWN;
                    if(value.track0 && value.track0[0].thumbnail_url) {
                        value.meta.thumbnail_url = value.track0[0].thumbnail_url;
                    } else {
                        value.meta.thumbnail_url = false;
                    };
                    var g = new ing.elements.moduleRow(value.meta);
                    var attached = ing.elements.attach(g, $('.'+moduleId));

                    if(moduleId !== undefined && loadModule == value.meta.id) {
                        active = attached;
                    }

                    ing.data.modules[value.meta.id] = value;
                });

                $('#id_owner').change();

                if(active) {
                    active.click();
                }

                //parseModulesAssignment();
                Ing.findInDOM().helpers.opaque_throbber($('.'+ moduleId), 'remove');
            });
        }
    },
    /**
     * Module management functions
     */
    this.mm = {
        parent: this,

        /**
         * Displaying module's details in a form
         */
        displayModuleDetails: function(htmlRef) {
            var ing = Ing.findInDOM();
            ing.helpers.throbber($('#mngMyModulesDetailsWrapper'));
            $.get(
            '/content/modules/' + ing.data.map[htmlRef.attr('id')].id + '/?format=json', function(data) {
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                $('#moduleTitle').val($.unescapifyHTML(data.meta.title));
                $('#moduleObjective').val(data.meta.objective?$.unescapifyHTML(data.meta.objective):"");
                $('#completionMsg').each(initCKEditorHandler);
                $('#completionMsg').val(data.meta.completion_msg?$.unescapifyHTML(data.meta.completion_msg):"");

                
                $('.preview').html('<span>' + t.PREVIEW + '</span>');
//                $('.preview').append('');
                // --replace these values with real ones
                $('#moduleCD').text(ing.helpers.timestampToDate(data.meta.created_on, true));

                $('#moduleMD_wrapper, #modulePD_wrapper, #moduleDD_wrapper').hide();
                $('#moduleMD, #modulePD, #moduleDD').hide();
                if(data.meta.state_code == 1) {
                    $('#moduleMD_wrapper, #moduleMD').show();
                    $('#moduleMD').text(app.helpers.timestampToDate(data.meta.updated_on, true));
                } else if(data.meta.state_code <= 4) {
                    $('#modulePD_wrapper, #modulePD').show();
                    $('#modulePD').text(app.helpers.timestampToDate(data.meta.published_on, true));
                } else if(data.meta.state_code <= 7) {
                    $('#moduleDD_wrapper, #moduleDD').show();
                    $('#moduleDD').text(app.helpers.timestampToDate(data.meta.deactivated_on, true));
                }

                $('#allow_download').attr('checked', data.meta.allow_download);
                $('#allow_skipping').attr('checked', data.meta.allow_skipping);
                $('#sign_off_required').attr('checked', data.meta.sign_off_required);

                $('#id_language option[value=' + data.meta.language + ']').attr('selected', 'selected');
                $('#moduleDate').val(data.meta.expires_on ? ing.helpers.timestampToDate(data.meta.expires_on) : '');
                var temporary_tags = $.parseJSON(data.meta.groups_ids_can_be_assigned_to);
                ing.data.tags = [];
                $(ing.config.tagList).html('');
                for(var i = 0, len = temporary_tags.length; i < len; i++) {
                    var tName = $('#groupList option[value=' + temporary_tags[i] + ']').text();
                    if(temporary_tags[i]!=-2){
                        if(!tName) {
                            tName = $('#myGroupList option[value=' + temporary_tags[i] + ']').text();
                        }
                        if(tName) {
                            ing.data.tags.push({id: temporary_tags[i], name: tName});
                            var el = new ing.elements.tag(tName);
                            ing.elements.attach(el, ing.config.tagList);
                        }
                    }
                }

                $("#assignmentList").html('');
                $.each(data.meta.groups_names, function(index, value) {
                    $("#assignmentList").append("<li>" + value + "</li>")
                });

                $('#id_language').sb('refresh');
                Ing.findInDOM().helpers.throbber($('#mngMyModulesDetailsWrapper'), 'remove');
				$('#groupList').sb('refresh');
            });
        },
        /**
         * Loading user's modules for management.
         */
        loadModules: function(moduleId) {
            Ing.findInDOM().helpers.throbber($('.myModules'));
            var activeKey = 0, active;
            $.get('/content/modules/list/', function(data) {
                $('.myModules').html('');
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                var ing = Ing.findInDOM();

                ing.data.modules = {};
                // -- temporary data for visualisation
                $.each(data, function(index, value) {
                    value.meta.assignments = value.meta.groups_names.length || '0';
                    value.meta.status = Ing.findInDOM().data.states[value.meta.state_code];
		            ing.data.modules[value.meta.id] = value;
                });

                $.each(data, function(index, value) {
                    value.meta.className = (index == 0 ? 'first ' : '') + (index%2 ? 'odd' : 'even');
                    var g = new ing.elements.moduleManagerRow(value.meta);
                    var attached = ing.elements.attach(g, $('.myModules'));
                    if(moduleId !== undefined && moduleId == value.meta.id) {
                        active = attached;
                        activeKey = index;
                    }
                    index++;
                });

                if(active) {
                    $("#mngMyModulesDetailsWrapper").show();
                    active.click();
                    // $('#myModules').animate({
                        // scrollTop: $(active).outerHeight() * activeKey - $('#myModules').height()/2
                        // },
                        // 300
                    // );
                } else {
                    $("#mngMyModulesDetailsWrapper").hide();

                }

                if($('#id_owner')) {
                    $('#id_owner').change();
                }

                Ing.findInDOM().helpers.throbber($('.myModules'), 'remove');
            });
        },
        /**
         * Saving module's details
         */
        saveModule: function() {
            var ing = Ing.findInDOM();
            var url = '/content/';
            var data = {
                'module_id': ing.data.activeModule.id,
                'title': $('#moduleTitle').val(),
                'objective': $('#moduleObjective').val(),
                'completion_msg': $('#completionMsg').data('editor').getData(),
                'language': $('#id_language').val(),
                'expires_on': $('#moduleDate').val(),
                'allow_download': $('#allow_download').is(':checked') ? 'checked' : '',
                'allow_skipping': $('#allow_skipping').is(':checked') ? 'checked' : '',
                'sign_off_required': $('#sign_off_required').is(':checked') ? 'checked' : '',
            }
            var groups_ids = [];
            $(ing.data.tags).each( function() {
                if(ing.data.groups[this.name]) {
                    groups_ids.push(ing.data.groups[this.name]);
                }
            });
            data.groups_ids = groups_ids;
            ing.helpers.throbber($('#mngMyModulesDetailsWrapper'));
            $.ajax({
                type: "POST",
                async: false,
                url: url,
                data: JSON.stringify(data),
                success: function(data) {
                    if(typeof data != 'object') { // IE bug --
                        data = $.parseJSON(data);
                    }
                    var windowHash=window.location.hash;
                                    ing.mm.loadModules(windowHash=windowHash.slice(1, windowHash.length));
                    Ing.findInDOM().helpers.throbber($('#mngMyModulesDetailsWrapper'), 'remove');
                }
            });
        },
        /**
         * Sets an active module as a global accessible variable
         */
        setActiveModule: function(htmlRef) {
            var ing = Ing.findInDOM();
            ing.data.activeModule = ing.data.map[htmlRef.attr('id')];

            $("#mngMyModulesDetailsWrapper").show();
						//$('#groupList').sb('refresh');
        }
    },
    /**
     * Reports view functions
     */
    this.reports = {
        parent: this,
        /**
         * Loads details of a given report
         */
        loadReportDetails: function(event, object) {
            $(object).siblings().removeClass('active');
            $(object).addClass('active');
            if ($('#reportDetails').length > 0) {
	            $('#reportDetails').show();
	            $('#runReport').removeClass('button-disabled').text(t.RUN_NOW);
	            $('#reportDetailsWrapper').html(
	            this.parent.elements.getObj(
	                new this.parent.elements.reportDetails(
	                this.parent.data.map[$(object).attr('id')])));
	            this.parent.data.activeReport = this.parent.data.map[$(object).attr('id')];

	            if (this.parent.data.activeReport.is_deleted)
	            	$('#runReport').hide();
	            else
	            	$('#runReport').show();

	            if(objSize(this.parent.data.activeReport.results)) {
	                $('#reportFilesWrapper').show();
	                $('#reportFilesList').html('');
	                var i = 0;
	                var ing = Ing.findInDOM();
	                var tmp = [];
	                $.each(this.parent.data.activeReport.results, function(key, value) {
	                    tmp.push(value);
	                });
	                tmp.sort(function(a,b){return b.id - a.id});
	                $.each(tmp, function(key, value) {
	                    value.className = i++%2 ? 'even' : 'odd';
	                    ing.elements.attach(new ing.elements.reportFileRow(value), $('#reportFilesList'));
	                });
	                $('#reportFilesList li:first').addClass('first');
	                $('#reportFilesList li:last').addClass('last');
	            } else {
	                $('#reportFilesWrapper').hide();
	            }
            }
            else {
	            $('#importedReportDetails').show();
	            $('#importedReportDetailsWrapper').html(
	            this.parent.elements.getObj(
	                new this.parent.elements.importedReportDetails(
	                this.parent.data.map[$(object).attr('id')])));
	            this.parent.data.activeReport = this.parent.data.map[$(object).attr('id')];
	            if(objSize(this.parent.data.activeReport.results)) {
	                $('#reportFilesWrapper').show();
	                $('#reportFilesList').html('');
	                var i = 0;
	                var ing = Ing.findInDOM();
	                var tmp = [];
	                $.each(this.parent.data.activeReport.results, function(key, value) {
	                    tmp.push(value);
	                });
	                tmp.sort(function(a,b){return b.id - a.id});
	                $.each(tmp, function(key, value) {
	                    value.className = i++%2 ? 'even' : 'odd';
	                    ing.elements.attach(new ing.elements.reportFileRow(value), $('#reportFilesList'));
	                });
	                $('#reportFilesList li:first').addClass('first');
	                $('#reportFilesList li:last').addClass('last');
	            } else {
	                $('#reportFilesWrapper').hide();
	            }
            }
        },
        /**
         * Loads reports list
         */
        loadReports: function(reportId) {
            var ing = Ing.findInDOM(), active;
            if ($('#reportsList').length > 0) {
            	ing.helpers.throbber($('#reportsList'));
	            $.get(
	            '/reports/list/', function(data) {
	                if(typeof data != 'object') { // IE bug --
	                    data = $.parseJSON(data);
	                }
	                var ing = Ing.findInDOM();
	                var reports = [];
	                ing.data.reports = data;
	                $.each(ing.data.reports, function(key, value) {
	                    reports.push(value);
	                });
	                reports = reports.sort( function(a,b) {
	                    return b.id > a.id
	                });
	                var i = 0;
	                $('#reportsList').html('');
	                var tmp = [];
	                $.each(reports, function(key, value) {
	                    tmp.push(value);
	                });
	                tmp.sort(function(a,b){return b.id - a.id});
	                $.each(tmp, function(key, value) {
	                    value.className = i++%2 ? 'even' : 'odd';
	                    var attached = ing.elements.attach(new ing.elements.reportRow(value), $('#reportsList'));
	                    if(reportId !== undefined && reportId == value.id) {
	                        active = attached;
	                    }
	                });
	                if(active) { active.click(); }
	                $('#reportsList li:first').addClass('first');
	                $('#reportsList li:last').addClass('last');
	                ing.helpers.throbber($('#reportsList'), 'remove');
	            });
	    	}
	    	else {
	    		if (!!!document.getElementById('importedReportsList')) { return; }
	    		ing.helpers.throbber($('#importedReportsList'));
	    		$.get(
	            '/administration/reports/list/', function(data) {
	                if(typeof data != 'object') { // IE bug --
	                    data = $.parseJSON(data);
	                }
	                var ing = Ing.findInDOM();
	                var reports = [];
	                ing.data.reports = data;
	                $.each(ing.data.reports, function(key, value) {
	                    reports.push(value);
	                });
	                reports = reports.sort( function(a,b) {
	                    return b.id > a.id
	                });
	                var i = 0;
	                $('#importedReportsList').html('');
	                var tmp = [];
	                $.each(reports, function(key, value) {
	                    tmp.push(value);
	                });
	                tmp.sort(function(a,b){return b.id - a.id});
	                $.each(tmp, function(key, value) {
	                    value.className = i++%2 ? 'even' : 'odd';
	                    ing.elements.attach(new ing.elements.reportTemplateRow(value), $('#importedReportsList'));
	                });
	                $('#importedReportsList li:first').addClass('first');
	                $('#importedReportsList li:last').addClass('last');
	                ing.helpers.throbber($('#importedReportsList'), 'remove');
	            });
	    	}
        }
    },
    /**
     * Helper functions. Handle multiple tasks.
     */
    this.helpers = {
        parent: this,
        /**
         * Autocompleting tags
         *
         * Autocompleting overriden due to functionality change
         */
        autocomplete: function(id) {
            $(id).autocomplete({
                source : function(request, response) {
                    $.get(
                    "/tagging/tags/autocomplete/",
                    { term: $.trim(request.term)},
                    response
                    );
                },
                focus: function() {
                    return false;
                },
                search: function() {
                    if(this.value.length < 3 || $.trim(this.value) == '') {
                        return false;
                    }
                }
            });
        },
        /**
         * Returns a key name from it's charcode
         */
        cc: function(code) {
            code = parseInt(code);
            switch(code) {
                case 8:
                    return 'BACKSPACE';
                case 9:
                    return 'TAB';
                case 13:
                    return 'ENTER';
                case 16:
                    return 'SHIFT';
                case 17:
                    return 'CTRL';
                case 18:
                    return 'ALT';
                case 27:
                    return 'ESC';
                case 32:
                    return 'SPACE'
                case 37:
                    return 'LEFT';
                case 38:
                    return 'UP';
                case 39:
                    return 'RIGHT';
                case 40:
                    return 'DOWN';
                default:
                    return String.fromCharCode(code);
            }
        },
        /**
         * Checking whether an observed form has any unsaved changes.
         * If any are found, a prompt is displayed. User can accept changes
         * or leave the form unchanged. After closing modal window, a callback
         * function passed as a parameter will be called.
         *
         * Important: In order to avoid unexpected behaviour, callback and
         * saveingAction should be declared as anonumous functions, eg.:
         *
         * Wrong way: checkForm(some_function())
         * some_function will be called BEFORE checking the form
         *
         * Right way: checkForm(function(){some_function()})
         * some_function will be called AFTER checking the form
         */
        checkForm: function(msg, savingAction, callback, validateAction) {
            var ing = this.parent;
            if(ing.data.dirtyForm) {
                ing.helpers.window(t.SYSTEM_MESSAGE,
                msg,
                [{
                    'text': t.YES,
                    events: [{
                        name: 'click',
                        handler: function() {
                            if(validateAction && !validateAction()) {
                                $.nmTop().close();
                                return false;
                            }

                            savingAction();
                            ing.data.dirtyForm = false;
                            $.nmTop().close();
                            callback();
                            return false;
                        }
                    }]
                },{
                    'text': t.NO,
                    events: [{
                        name: 'click',
                        handler: function() {
                            ing.data.dirtyForm = false;
                            $.nmTop().close();
                            callback();
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
                )
            } else {
                callback();
            }
        },
        /**
         * Calculates width of a shelf's
         * or a module's html wrapper.
         */
        computeWidth: function(itemId) {
            var tmp = 0;
            var cnf = this.parent.config;
            $('#' + itemId + ' li').each( function(index, elem) {
                tmp += $(elem).width() + (itemId == 'module' ? 30 : 15) /* -- bad CSS ! -- */;
            });
            tmp += cnf.elemWrapperWidth;
            eval(itemId +'Width = ' + tmp);
            $('#' + itemId).css('width', tmp);
            $(cnf.sound).css('width', $(cnf.module).width() + 'px');
            $(cnf.sound).children('.ui-resizable').each( function(element) {
                var x = $(this).position().left + $(this).width();
                if(x > $(cnf.sound).width() - cnf.elemWrapperWidth) {
                    $(this).remove();
                }
            });
			var elements = $('#' + itemId).find('li').length;
			var container = $('#' + itemId).parent();
			if (elements < 6) {
				$(container).siblings(".prev, .next").addClass('disabled');
			} else {
				$(container).siblings(".prev, .next").removeClass('disabled');
			}

        },
        /**
         * Cookie getter and setter
         */
        cookie: {
            get: function(name) {
                var match = (' ' + document.cookie).match(new RegExp('[; ]' + name + '=([^\\s;]*)'));
                return (name && match) ? unescape(match[1]) : '';
            },
            set: function(name, value, secs) {
                var today = new Date();
                var expire = new Date();
                expire.setTime(today.getTime() + 1000 * secs);
                document.cookie = name + "=" + escape(value) + "; " +
                "expires="+expire.toGMTString() + "; " +
                "path=/";
            }
        },
        /**
         * Displays file's details in a html wrapper
         */
        displayDetails: function(obj, editable) {
            if(obj) {
                var els = this.parent.elements;
                var note = obj.note;
                if (note.length > 50)
                	obj.shortText = note.substr(0, 50) + "...";
                else
                	obj.shortText = note;
                var details = new els.details(obj, editable);
                $('#fileDetails').html('');
                els.attach(details, $('#fileDetails'));
                $('#fileDetails .taglist li').draggable({
                    helper: function(event, element) {
                        var clone = $(event.target);
                        return $('<div class="taglistHelper"></div>').html( clone.html() );
                    },
                    'appendTo': 'body'
                });
                $('#fileDetails .contentNote').tooltip({position: "bottom center", effect: 'slide'});
            }
        },
        /**
         * Finds an appropriate file object within
         * a filelist stored in an App object
         */
        find: function(search) {
            for(var i = 0, len = this.parent.data.files.length; i < len; i++) {
                if(this.parent.data.files[i].id == search) {
                    return i;
                }
            }
            return false;
        },
        /**
         * Returns actual date and time in YYYY-MM-DD HH:ii:ss format
         */
        getNow: function() {
            var now = new Date();
            return now.getFullYear() + '-' + this.lz(now.getMonth() + 1) + '-' + this.lz(now.getDate()) + ' '
            + this.lz(now.getHours()) + ':' + this.lz(now.getMinutes()) + ':' + this.lz(now.getSeconds());
        },
        /**
         * Displays notification on a HTML console.
         * This is a temporary function.
         *
         * @todo: Remove after finishing prototype.
         */
        js_notify: function(msg, type) {
            //console.log(msg);
            // $('#msgs').prepend($('<div class="' + type + '"><span class="date">' + this.getNow() + '</span> ' + msg + '</div>'));
        },
        /**
         * Adds a leading zero to a number
         */
        lz: function(s) {
            return String(s).length == 1 ? "0" + s : s;
        },
        /**
         * Finds maxiumum z-index attribute within
         * document's object.
         *
         * WARNING: This function can be VERY resource
         * consuming - should be used wisely
         */
        maxZIndex: function(){
            var maxZ = Math.max.apply(null,$.map($('body *'), function(e,n){
                if($(e).css('position')=='absolute'){
                    return parseInt($(e).css('z-index'))||1 ;
                }
            }));
            maxZ = Math.max(maxZ, 1); // -- patch for IE bug
            return maxZ;
        },
        /**
         * Moves shelf and module left or right.
         */
        move: function(dir, step, itemId) {
            var w = parseInt($(itemId).css('width'));
            var ing = Ing.findInDOM();
            var eventTriggered = false;
            if(w > ing.config.shelfWrapperWidth) {
                if(dir == 'right') {
                    step = -step;
                }
                $(itemId).css('left', (parseInt($(itemId).css('left')) + step) + 'px');
                if(parseInt($(itemId).css('left')) > 0) {
                    ing.triggerEvent('shelfStart', [[itemId]]);
                    eventTriggered = true;
                    $(itemId).css('left', '0px');
                }else{
                    ing.triggerEvent('shelfMoving', [[itemId, dir]]);
                }
                if(parseInt($(itemId).css('left')) < -(w - $(itemId + 'Wrapper').width())) {
                    ing.triggerEvent('shelfStop', [[itemId]]);
                    $(itemId).css('left', -(w - $(itemId + 'Wrapper').width()) + 'px');
                }else if(!eventTriggered){
                    ing.triggerEvent('shelfMoving', [[itemId, dir]]);
                }
            }
        },
        /**
         * Throbber overlay. Indicates background operation
         * affecting given HTML element. Function attaches
         * and detaches throbber layer to a given HTML object.
         */
        throbber: function(element, mode) {
            if(mode == 'remove') {
                $('#throbber_' + ($(element).attr('id') || '')).remove();
                return true;
            }
            var e = $(element);
            var t = this.parent.elements.getObj(new this.parent.elements.throbber(e.attr('id') || ''));
            var p = e.offset();
            t.css({
                height: e.outerHeight(),
                left: p.left,
                'line-height': e.outerHeight() + 'px',
                top: p.top,
                width: e.outerWidth(),
                zIndex: this.parent.helpers.maxZIndex() + 1
            });
            t.appendTo($('body'));
        },
        /**
         * Throbber overlay. Indicates background operation
         * affecting given HTML element. Function attaches
         * and detaches throbber layer to a given HTML object.
         */
        opaque_throbber: function(element, mode) {
            if(mode == 'remove') {
                $('#throbber_' + ($(element).attr('id') || '')).remove();
                this.throbber(element, mode);
                return true;
            }
            var e = $(element);
            var t = this.parent.elements.getObj(new this.parent.elements.opaque_throbber(e.attr('id') || ''));
            var p = e.offset();
            t.css({
                height: e.outerHeight(),
                left: p.left,
                'line-height': e.outerHeight() + 'px',
                top: p.top,
                width: e.outerWidth(),
                zIndex: this.parent.helpers.maxZIndex() + 1
            });
            t.appendTo($('body'));
            this.throbber(element, mode);
        },
        /**
         * Converts timestamp to date string
         */
        timestampToDate: function(ts, addTime) {
            var d = new Date(ts * 1000);
            var hlp = this.parent.helpers;
            return d.getFullYear() + '-' + hlp.lz(d.getMonth() + 1) + '-' + hlp.lz(d.getDate()) +
            (addTime ? ' ' + hlp.lz(d.getHours()) + ':' + hlp.lz(d.getMinutes()) : '');
        },
        /**
         * Other procedures and events that need to be
         * initialized upon app startup.
         */
        tools: function() {
            var cnf = this.parent.config,
            	oth = cnf.other,
            	mv = this.parent.helpers.move,
            	moved1 = false,
            	moved2 = false;
            
            $(oth.mr).mousedown( function() {
                oth.timer2 = setInterval( function() {
                    mv('right', oth.movingStep, cnf.module);
                    moved2 = true;
                }, oth.movingInterval);
            });
            $(oth.ml).mousedown( function() {
                oth.timer2 = setInterval( function() {
                    mv('left', oth.movingStep, cnf.module);
                    moved2 = true;
                }, oth.movingInterval);
            });
            $(oth.mr + ', ' + oth.ml).mouseup( function() {
            	if (!moved2) {
                	var dir = $(this).hasClass('next') ? 'right' : 'left';
                	mv(dir, 60, cnf.module);
            	}
                clearTimeout(oth.timer2);
                moved2 = false;
            });
            $(oth.sr).mousedown( function() {
                oth.timer = setInterval( function() {
                    mv('right', oth.movingStep, cnf.shelf);
                    moved1 = true;
                }, oth.movingInterval);
            });
            $(oth.sl).mousedown( function() {
                oth.timer = setInterval( function() {
                    mv('left', oth.movingStep, cnf.shelf);
                    moved1 = true;
                }, oth.movingInterval);
            });
            $(oth.sr + ', ' + oth.sl).mouseup( function() {
            	if (!moved1) {
                	var dir = $(this).hasClass('next') ? 'right' : 'left';
                	mv(dir, 60, cnf.shelf);
            	}
                clearTimeout(oth.timer);
                moved1 = false;
            });

            //Getting JSON data for "Continue course" menu
            var continueCourseId;
            var continueSegmentId
            var menuContinue = $('#menuModules.continueCourse').parent('a');

            menuContinue.click(function() {
                $(document).unbind('ajaxError');
                $.ajax({
                    url : "/tracking/course_to_continue/",
                    cache: false,
                    success : function(json, statusText){
                        continueCourseId = json.course_id;
                        continueSegmentId = json.segment_id;
                        //menuContinue.attr('href', '/content/view/' + continueCourseId + '/#/' + continueSegmentId);
                        location.href='/content/view/' + continueCourseId + '/#/' + continueSegmentId;
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        var ing = Ing.findInDOM();
                        ing.helpers.window(
                            t.SYSTEM_MESSAGE, t.NO_COURSE_TO_CONT,
                            [{
                                text: t.CLOSE_WINDOW,
                                events: [{
                                    name: 'click',
                                    handler: function(e) {
                                        $.nmTop().close();
                                        return false;
                                    }
                                }]
                            }]
                        );
                    }
                });
            });

        },
        /**
         * Adds trimming functionality to a textarea.
         *
         * After a maximum length of entered text has been reached,
         * no new text can be entered.
         * Optionally, a counter with information about number of
         * characters left can be displayed.
         */
        trimming: function(obj, length, addCounter) {
            obj.live('keyup', function() {
                if ($(this).val().length > length) {
                    $(this).val($(this).val().substr(0, 400));
                }
                if(addCounter) {
                    if(!($('.charCounter').size())) {
                        if($(this).parent('.inputWrapper').length){
                           $(this).parent('.inputWrapper').after('<span class="charCounter"></span>');
                        }else{
                           $(this).after('<span class="charCounter"></span>');
                        }

                    }
                    var len = length - $(this).val().length;
                    $('.charCounter').text(len + ' ' + (len != 1 ? t.CHARS_LEFT : t.CHAR_LEFT));
                }
            });
        },
        /**
         * Simple window. Can be used as a modal window, as an app window or as
         * a prompt.
         * A default window can be invoked as folllows:
         *
         * Ing.findInDOM().helpers.window('Window title', 'Window content', buttons_array, boolean = false)
         *
         * @see: window element comment for more details
         */
        window: function(title, msg, buttons, hideClosingButton, afterCloseAction) {
            var els = this.parent.elements;
            var win = els.getObj(new els.window({title: title, msg: msg}, buttons, hideClosingButton, afterCloseAction));
            win.appendTo($('body'));
            $('<a href="#' + win.attr('id') + '"></a>').nyroModal().trigger('click');
        },
        taglist: function() {
    	    var tagList = $('#createModule #tagList');
		    var label_width = $(tagList).siblings('label').width();
		    var input_width = $(tagList).siblings('.inputWrapper').width();
		    var li_width = $(tagList).parent().width();
		    $(tagList).width(li_width - label_width - input_width - 35);
        },
        htmlSpecialDecoder: function(input){
        	return input.replace(/&gt;/gi, '>').replace(/&lt;/gi, '<')
						.replace(/&amp;/gi, '&').replace(/&nbsp;/gi, ' ');
        }
    },
    /**
     * App listeners - a collection of listeners for
     * all app's events
     */
    this.listeners = {
        parent: this,
        /**
         * Listens to any changes in shelf or a module
         * and sends request to a backend saving script
         */
        changeListener: function() {
            $(this.parent).bind('itemChanged', function(event, id) {
                this.callbacks.saveChanges(id);
            });
        },
        /**
         * Changes made on a group list
         */
        groupChangeListener: function() {
            $(this.parent).bind('groupListChange', function(event, id) {
                if(id == 'groups') {
                    $('#narrow').val('');
                } else {
                    $('#narrow2').val('');
                }
                var targets = {groups: 'grouplist', my_groups: 'userlist'};
                var index = $('#' + id).val();
                var ing = Ing.findInDOM();
                var users = ing.data.memberships;
                $('#' + targets[id]).html('');
                if(users[index] == undefined) {
                    users[index] = [];
                }

                var gArray = new Array();
                for(var i = 0, len = users[index].length; i < len; i++) {
                    gArray.push( ing.data.users[users[index][i]] );
                }
                gArray.objSort("role","last_name");
								//console.log(gArray);
                for(var i = 0, len = users[index].length; i < len; i++) {
                    var g = new ing.elements.userItem(gArray[i]);
                    ing.elements.attach(g, $('#' + targets[id]));
                }

                //for(var i = 0, len = users[index].length; i < len; i++) {
                //    var g = new ing.elements.userItem(ing.data.users[users[index][i]]);
                //    ing.elements.attach(g, $('#' + targets[id]));
                //}
                if(id == 'my_groups') {
                    if(index == 0) {
                        $('#ge').addClass('button-disabled').removeClass('button-normal');
                        $('#gr').addClass('button-disabled').removeClass('button-normal');
                    } else {
                        $('#ge').removeClass('button-disabled').addClass('button-normal');
                        $('#gr').removeClass('button-disabled').addClass('button-normal');
                    }
                }
            });
        },
        /**
         * Filtering users view within given group.
         *
         * @todo: Decide whether hidden user loses selection or not.
         */
        groupFilterListener: function() {
            $(this.parent).bind('groupFiltered', function(event, id) {
                var target = id == 'narrow' ? 'grouplist' : 'userlist'
                $('#' + target + ' option').each( function() {
                    if($(this).html().toLowerCase().indexOf($('#' + id).val().toLowerCase()) == -1) {
                        $(this).remove();
                    }
                })
            });
        },
        /**
         * Moving users to new group
         */
        groupMoveUsersListener: function() {
            $(this.parent).bind('usersMoved', function(event) {
                var groupId = $('#my_groups').val();
                var groupsListId = $('#groups').val();
                if(groupId == 0) {
                    Ing.findInDOM().helpers.window(t.SYSTEM_MESSAGE, t.CHOOSE_GROUP_LIST);
                    return false;
                }
                var data = {'action': 'add', members: []};
                var append = [];
                var users = Ing.findInDOM().data.memberships;
                $('#grouplist option:selected').each( function(e, elem) {
                    var element = {id: $(elem).val(), username: $(elem).html()};
                    var push = true;
                    for(var i=0, len = users[groupId].length; i<len; i++) {
                        if (users[groupId][i] == element.id) {
                            push = false;
                        }
                    }
                    if(push) {
                        data.members.push(element.id * 1);
                        append.push($(elem).clone());
                    }

                    if(groupsListId == -2) {
                        if(users[groupsListId].inArray($(elem).val())) {
                            for( var i = 0, len = users[groupsListId].length; i < len; i++) {
                                if(users[groupsListId][i] == $(elem).val()) {
                                    users[groupsListId].splice(i, 1);
                                    break;
                                }
                            }
                            $(elem).remove();
                        }
                    }
                });
                if(data.members.length > 0) {
                    Ing.findInDOM().helpers.throbber($('#userlistWrapper'));
                    $.post(
                    '/management/groups/' + groupId + '/members/',
                    JSON.stringify(data), function(data) {
                        if(typeof data != 'object') { // IE bug --
                            data = $.parseJSON(data);
                        }
                        if(data.status == 'OK') {
                            $.each(append, function(key, value) {
                                value.appendTo($('#userlist'));
                                users[groupId].push(value.val() * 1);
                            });
                            if(append.length == 1) {
                                Ing.findInDOM().gm.refreshUserDetails(append[0].val(), true);
                            }
                        } else {
                            // -- tutaj obsulzyc blad dodawania
                        }
                        Ing.findInDOM().helpers.throbber($('#userlistWrapper'), 'remove');
                    });
                }
            });
        },
        /**
         * Removing users from group
         */
        groupRemoveUsersListener: function() {
            $(this.parent).bind('groupRemoveUsers', function(event) {
                var users = Ing.findInDOM().data.memberships;
                var groupId = $('#my_groups').val();
                var data = {'action': 'remove', members: []};
                var append = [];

                var inLastGroup = [];
                $('#userlist option:selected').each( function(e, elem) {
                    var id = $(elem).val();

                    var count = 0;
                    var groupCount = jQuery.each(users, function(groupId, members) {
                        if(groupId > 0 && jQuery.inArray(parseInt(id), members) > -1) {
                            count++;
                        }
                    });

                    if(count == 1) {
                        inLastGroup.push($.trim($(elem).text()));
                    }

                    append.push($(elem));
                    data.members.push(id);
                });

                if(inLastGroup.length > 0) {
                    app.helpers.window(t.SYSTEM_MESSAGE, t.CANNOT_REMOVE_THESE_USERS_FROM_THEIR_LAST_GROUP + ": " + inLastGroup.join((", ")));
                    return;
                }

                if(data.members.length > 0) {
                    Ing.findInDOM().helpers.throbber($('#userlistWrapper'));
                    $.post(
                    '/management/groups/' + $('#my_groups').val() + '/members/',
                    JSON.stringify(data), function(data) {
                        if(typeof data != 'object') { // IE bug --
                            data = $.parseJSON(data);
                        }
                        if(data.status == 'OK') {
                            $.each(append, function(key, value) {
                                for( var i = 0, len = users[$('#my_groups').val()].length; i < len; i++) {
                                    if(users[$('#my_groups').val()][i] == value.val()) {
                                        users[$('#my_groups').val()].splice(i, 1);
                                        break;
                                    }
                                }
                                /* adding element to no-group if user does
                                    not belong to any groups
                                 */
                                var add_no_group = true;
                                $('#my_groups option').each(function() {
                                    var group_val = $(this).val();
                                    if((group_val > 0) && (users[group_val] != undefined)) {
                                        if(users[group_val].inArray(value.val())) {
                                            add_no_group = false;
                                            return false;
                                        }
                                    }
                                });
                                if(add_no_group == true) {
                                    var groupsListId = $('#groups').val();
                                    if(groupsListId == -2) {
                                        value.appendTo($('#grouplist'));
                                    }
                                    users[-2].push(value.val() * 1);
                                }
                            });
                            $('#userlist option:selected').remove();
                            if(append.length == 1) {
                                Ing.findInDOM().gm.refreshUserDetails(append[0].val());
                            }
                        } else {
                            // -- tutaj obsulzyc blad dodawania
                        }
                        Ing.findInDOM().helpers.throbber($('#userlistWrapper'), 'remove');
                    });
                }
            });
        },
        /*
            Clicked setting user group manager rights.
         */
        toggleUserGroupManagerListener: function() {
            $(this.parent).bind('toggleUserGroupManager', function() {
                var cnf = app.config;
                var userId = Ing.findInDOM().data.activeUser.id;
                var groupId = $('#my_groups').val();
                if(userId){
                  $.post(
                   '/management/users/' + userId + '/'+groupId+'/',
                   '',
                    function(data, status, xmlHttpRequest){
                        var user = Ing.findInDOM().data.users[userId];
                        if(user.manages.inArray(groupId)) {
                            var adding = true;
                            $.each(user.manages, function(v, val){
                            if(user.manages[v]==groupId) {
                                user.manages = user.manages.splice(v,1);
                                adding = false;
                                return false;
                            }
                            });
                            if(adding) {
                                user.manages.push(groupId);
                            }
                        }
                    app.gm.saveState();
                    app.gm.loadData();
                    $('#u_details_content').html(t.NO_USER_SELECTED);
                    app.helpers.window(t.SYSTEM_MESSAGE, t.USER_GROUP_MANAGEMENT);
                   });
                   return false;
                }
                return false;
            });
        },
        /**
         * Selecting user on a list
         */
        groupUserSelectedListener: function(id) {
            $(this.parent).bind('userSelected', function(event, id) {
                if($('#' + id + ' option:selected').length > 1) {
                    $('#u_details_content').html(t.SELECTED_USERS + ': ' + $('#' + id + ' option:selected').length);
                } else if($('#' + id + ' option:selected').length == 1) {
                    var e = $('#' + id + ' option:selected');
                    var ing = Ing.findInDOM();
                    ing.gm.refreshUserDetails(e.val(), id == 'userlist');
                }
            });
        },
        /**
         * Listens to changes within reports list
         */
        reportsChangeListener: function() {
            $(this.parent).bind('reportChanged', function(event, object) {
                this.reports.loadReportDetails(event, object);
            });
        },
        /**
         * Bind to tag input field. Listenes to any
         * value changes made to it.
         */
        tagsListener: function() {
            $(this.parent).bind('keyup', function(event) {
                this.callbacks.handleTags(event);
            }).bind('tagRemoved', function(event, tag) {
                this.callbacks.handleTagRemoval(event, tag);
            });
        },
        /**
         * Bind to search form. Listens to submit event.
         */
        formSubmitListener: function() {
            $(this.parent).bind('submit_search', function(event) {
                this.callbacks.handleFormSubmit(event);
            });
        },
        /**
         * enable self registation for groups
         */
        enableGroupsSelfRegisterListener: function() {
            $(this.parent).bind('enableGroupsSelfRegister', function(event) {
                var data = {'action': 'enable', groups: []};
                var append = []
                $('#all_group_list option:selected').each( function(e, elem) {
                    var id = $(elem).val();
                    data.groups.push(id);
                    append.push($(elem));
                });

                if(data.groups.length > 0) {
                    $.post(
                    '/management/groups/selfregister/',
                    JSON.stringify(data), function(data) {
                        if(typeof data != 'object') { // IE bug --
                            data = $.parseJSON(data);
                        }
                        if(data.status == 'OK') {
                            $.each(append, function(key, value) {
                                $(value, '#all_group_list').each(function() {
                                    $(this).remove();
                                });
                                $('#self_register_group_list').append(value);
                            });
                        } else {
                            // -- tutaj obsulzyc blad dodawania
                        }
                    });
                }
            });
        },
        /**
         * disable self registation for groups
         */
        disableGroupsSelfRegisterListener: function() {
            $(this.parent).bind('disableGroupsSelfRegister', function(event) {
                var data = {'action': 'disable', groups: []};
                var append = []
                $('#self_register_group_list option:selected').each( function(e, elem) {
                    var id = $(elem).val();
                    data.groups.push(id);
                    append.push($(elem));
                });

                if(data.groups.length > 0) {
                    $.post(
                    '/management/groups/selfregister/',
                    JSON.stringify(data), function(data) {
                        if(typeof data != 'object') { // IE bug --
                            data = $.parseJSON(data);
                        }
                        if(data.status == 'OK') {
                            $.each(append, function(key, value) {
                                $(value, '#self_register_group_list').each(function() {
                                    $(this).remove();
                                });
                                $('#all_group_list').append(value);
                            });
                        } else {
                            // -- tutaj obsulzyc blad dodawania
                        }
                    });
                }
            });
        },

    },
    /**
     * Module element
     * @todo: proper playback mode
     */
    this.module = {
        parent: this,
        /**
         * Adds an item to a module
         */
        addItem: function(item, type, readOnly) {
            var cnf = this.parent.config;
            var els = this.parent.elements;
            var id = cnf.module;
            var root = $(cnf.module).children('ul');

            if(type == 'segment') {
                if(readOnly) {
                    els.attach(new els.plainSegment(item), root);
                    $(id).css('width', parseInt($(id).width()) + cnf.elemWrapperWidth + 10);
                } else {
                    els.attach(new els.segment(item), root);
                    $(id).css('width', parseInt($(id).width()) + cnf.elemWrapperWidth);
                    $(cnf.sound).css('width', $(id).width());
                }
            } else {
                if(readOnly) {
                    //var snd = els.getObj(new els.plainSound(item));
                } else {
                    var snd = els.getObj(new els.sound(item));
                    this.parent.addInterfaces(snd);

                    snd.css({
                        width: (item.end - item.start + 1) * cnf.elemWrapperWidth,
                        position: 'absolute',
                        left: (item.start * cnf.elemWrapperWidth)
                    });
                    snd.appendTo($(cnf.soundId));
                }
            }
        },
        /**
         * Binds click event to HTML segment items.
         * Clicking on a segment moves the player
         * index to clicked item.
         */
        addViewerEvents: function() {
            $(this.parent.config.module).find('a').live('click', function(elem) {
                var elements = $("#moduleList").find('li').length;
                if ( app.data.activeItem < elements ) {
                	Ing.findInDOM().player.api.pause();
                }
                Ing.findInDOM().player.play(this);
                return false;
            })
        },
        /**
         * Creates a module from JSON object
         */
        create: function(json, readOnly) {
            var json = $.parseJSON(json);
            if(json.meta.id) {
                this.parent.data.moduleId = json.meta.id;
            }
            var root = $(this.parent.config.module).children('ul');
            root.html('');
            for(var i = 0, len = json.track0.length; i < len; i++) {
                this.parent.module.addItem(json.track0[i], 'segment', readOnly);
            }
            for(var i = 0, len = json.track1.length; i < len; i++) {
                this.parent.module.addItem(json.track1[i], 'sound', readOnly);
            }
            if(readOnly) {
                if(this.parent.helpers.cookie.get('ing_obj_' + json.meta.id) == '') {
                	if (!!!singleModuleMode) this.displayObjective(json, false);
                    this.parent.helpers.cookie.set('ing_obj_' + json.meta.id, 1, this.parent.config.cookieTime);
                } else {
                    Ing.findInDOM().data.moviePlayed = true;
                }
            } else {
                $(this.parent.config.moduleTitle).val(json.meta.title);
                $(this.parent.config.moduleObjective).val(json.meta.objective);
            }
            this.parent.data.moduleJSON = json;
        },
        /**
         * Displays course objective in a modal window.
         *
         * If a modal window is shown, a player is not visible.
         * A callback attached to the closing button displays
         * the player and starts playback.
         */
        displayObjective: function(moduleObject, clickedButton) {
            var that = this;
            var objective = $.trim(moduleObject.meta.objective.substring(0,2200));

            if (objective) {
                this.parent.helpers.window(
                moduleObject.meta.title, '<span class="objectiveContent">'+objective+'</span>',
                [{
                    text: t.CLOSE_OBJECTIVE,
                    events: [{
                        name: 'click',
                        handler: function(e) {
                            $.nmTop().close();
//                            if (!clickedButton) { that.startPlayback(moduleObject.meta.id); }
                            that.parent.player.api.resume();
                            return false;
                        }
                    }]
                }]
                );
            }

            if(!objective) {
                objective = t.NO_OBJECTIVE;

                if ( clickedButton ) {
                    this.parent.helpers.window(
                    moduleObject.meta.title, '<span class="objectiveContent">'+objective+'</span>',
                    [{
                        text: t.CLOSE_OBJECTIVE,
                        events: [{
                            name: 'click',
                            handler: function(e) {
                                $.nmTop().close();
//                                if (!clickedButton) { that.startPlayback(moduleObject.meta.id); }
                                that.parent.player.api.resume();
                                return false;
                            }
                        }]
                    }]
                    );
                }

//                if(!clickedButton) {
//                    that.startPlayback(moduleObject.meta.id);
//                    return;
//                }
            }
            //playMovie('/content/modules/' + moduleObject.meta.id + '/?format=xml', 'playlist', false, playingIndex);
        },
        /**
         * Gets module details from the database and
         * creates it's HTML wrapper.
         */
        get: function(id, format, readOnly) {
            app.helpers.throbber('#moduleWrapper');
            if(!format) {
                format = 'json';
            }
            $.ajax({url: '/content/modules/' + id + '/?format='+format+'&token='+app.config.ocl_token,
            	cached: false,
	            success: function(data) {
	                app.helpers.throbber('#moduleWrapper', 'remove');
	                Ing.findInDOM().module.create(data, readOnly);
	            },
	            dataType: 'text',
	            async: false
            });
        },
        /**
         * Checks, whether two HTML elements overlap.
         */
        overlap: function(x1, w1, x2, w2) {
            if(x2 + w2 <= x1 || x1 + w1 <= x2) {
                return false;
            } else {
                return true;

            }
        },
        /**
         * Creates a JSON object from a module and passes it
         * to a backend saving function.
         */
        save: function() {
            // -- clearing form timer - only in prototype
            clearTimeout(formTimer);
            var cnf = this.parent.config;
            var mod = $(cnf.module);

            var json = {
                version: 1,
                meta: {
                    title: $(cnf.moduleTitle).val(),
                    objective: this.parent.data.moduleJSON ? this.parent.data.moduleJSON.meta.objective : ''
                },
                track0: [],
                track1: []
            }
            if(this.parent.data.moduleId) {
                json.meta.id = this.parent.data.moduleId;
            }
            var elems = mod.find('li').each( function(i) {
                var details = Ing.findInDOM().data.map[$(this).attr('id')];
                json.track0.push({
                    id: details.id || false,
                    start: i,
                    end: i
                });
            });
            var snds = mod.children(cnf.sound).children('div').each( function(i) {
                var details = Ing.findInDOM().data.map[$(this).attr('id')];
                var start = parseInt($(this).css('left')) / cnf.elemWrapperWidth;
                var end = parseInt($(this).css('width')) / cnf.elemWrapperWidth + start - 1;
                json.track1.push({
                    id: details.id || false,
                    start: start,
                    end: end,
                    'playback_mode': $(this).find('.sndMode').hasClass('repeat') ? 'repeat' : 'once'
                });
            });
            this.parent.callbacks.saveModule(json);
        },
        /**
         * Function run after dragging or resizing sound backgrounds.
         * Checks whether any two sound items overlap and cancels last
         * editing operation if they do.
         */
        snapBackOnOverlap: function(event, ui, elem) {
            var overlapFound = false;
            var ing = Ing.findInDOM();

            $(ing.config.sound).children().each( function() {
                var rs = this;
                var rs_pos = $(rs).position();
                var rs_width = $(rs).width();
                var rs_height = $(rs).height();
                if(!overlapFound && elem != rs && ing.module.overlap( rs_pos.left, rs_width,
                $(elem).position().left, $(elem).width() ) )
                    overlapFound = true;
            });
            if(overlapFound) {
                if(ui.originalSize) {
                    $(elem).css( {
                        'width' : ui.originalSize.width + 'px',
                        'height' : ui.originalSize.height + 'px'
                    });
                }
                var left = ing.data.temporaryDrag || ui.originalPosition.left + 'px';
                $(elem).css( {
                    'top' : ui.originalPosition.top + 'px',
                    'left' : left
                });
                ing.data.temporaryDrag = false;
            }
        },
        /**
         * Starts playback of a given module
         */
        startPlayback: function(id) {
            var mark = Ing.findInDOM().data.moviePlayed;
            if(!mark) {
                app.player.playEmbedded(id, 'playlist', false, playingIndex);
                mark = true;
            }
        },
        showHideSignOffButton: function(moduleId) {
            if($('#courseSignOff').length) {
                $.get(
                    '/content/show-sign-off-button/'+moduleId+'/?token=' + app.config.ocl_token,
                    function(data, status, xmlHttpRequest){
                        if(typeof data != 'object'){ // IE bug --
                            data = $.parseJSON(data);
                        }
                        if(data.status == 'OK' && data.show){
                            $('#courseSignOff').show();
                            return false;
                        } else {
                            $('#courseSignOff').hide();
                        }
                });
            }
        }
    },
    /**
     * HTML5/Flash player
     */
    this.player = {},
    /**
     * Roller object. Displays fileslist in a roller-style list.
     */
    this.roller = {
        parent: this,
        /**
         * Adds draggable interface to a given element.
         */
        addDraggable: function(elem) {
            $(elem).draggable({
				helper: function(event){
					var clone = $(event.target).parents('li');
					return $('<div class="mainHelper"></div>').attr('id', $(this).attr('id')).html(clone.html());
				},
                opacity: 0.5,
                placeholder: 'holds',
                appendTo: 'body',
                scroll: false,
                connectToSortable: '.ui-sortable',
                stop: function(event, ui) {
                    var ing = Ing.findInDOM();
                    var cnf = ing.config;
                    ing.helpers.computeWidth(cnf.shelf.substr(1));
                    ing.helpers.computeWidth(cnf.module.substr(1));
                }
            }).disableSelection();
        },
        /**
         * Adds scrollable interface to a given element.
         */
        addScrollable: function() {
            var cnf = this.parent.config;
            var that = this;
			var beforeIndex;
			var newIndex=1;
			var scr;
            $(cnf.roller).scrollable({
                circular: false,
                mousewheel: true,
				onBeforeSeek: function() {
						scr = that.scr();
						beforeIndex = scr.getIndex() + 1;
						//console.log( '[before:'+beforeIndex+']' );
						//console.log( '[after:'+newIndex+']' );
						if ( (beforeIndex != newIndex) || (newIndex === 'undefined') )
						{
								return false;
						}
				},
                onSeek: function() {
                    scr = that.scr();
					newIndex = scr.getIndex() + 1;
					//console.log( '[after:'+newIndex+']' );

                    $(cnf.rollerNavi).children('a').removeClass('active');
                    $(cnf.rollerNavi).children('#'+scr.getIndex()).addClass('active');
                    if(scr.getIndex() == scr.getSize() - 1) {
                        if(scr.getItems().last().children('li').length == 8) {
                            that.parent.loadFiles(true);
                        }
                    }
                    if(scr.getIndex() == 0) {
                        $('#rollerWrapper .prev').addClass('disabled');
                    } else {
                        $('#rollerWrapper .prev').removeClass('disabled');
                    }
                    if(scr.getIndex() >= scr.getSize() - 1) {
                        $('#rollerWrapper .next').addClass('disabled');
                    } else {
                        $('#rollerWrapper .next').removeClass('disabled');
                    }
                }
            })/*.navigator()*/;
        },
        /**
         * Clearing scroller object.
         */
        clear: function() {
            var items = this.scr().getItems();
            for(var i = items.length - 1; i > -1; i--) {
                items.eq(i).remove();
                //$(this.parent.config.rollerNavi).children('a').eq(i).remove();
            }
        },
        /**
         * A short function for returning scroller object.
         */
        scr: function() {
            return $(this.parent.config.roller).data('scrollable');
        }
    },
    /**
     * Shelf object. It is a part of create module screen
     */
    this.shelf = {
        parent: this,
        /**
         * Shows selected shelf
         */
        getIndex: function(shelfId){
            if(!shelfId){
                return 0;
            }else{
                var index = 0;
                $.each(this.parent.data.shelfs, function(i){
                    if(this.meta.id == shelfId){
                        index = i;
                    }
                });
                return index;
            }
        },
        /**
         * Removes shelf.
         */
        remove: function(){
            var url = '/content/collections/delete/' + this.parent.data.shelfId + '/';
            $.post(
                url,
                '', function(data) {
                    Ing.findInDOM().shelf.loadShelfs()
                });
        },
        /**
         * Load shelf list and creates their HTML representation
         */
        loadShelfs: function(sid){
            //this.parent.helpers.throbber('#shelfBigWrapper');
            var that = this;
            $.get(
                '/content/collections/',
                function(data){
                    if(data.length > 0){
                        that.parent.data.shelfs = data;
                        $('#shelfId').html('');
                        $.each(data, function(){
                            $('#shelfId').append('<option value="' + this.meta.id + '">' + this.meta.title + '</option>');
                        });
                        $('#shelfId').sb('refresh');
                        //that.parent.helpers.throbber('#shelfBigWrapper', 'remove');
                        that.parent.shelf.showShelf(sid);
                    }else{
                        $('#collectionCreate').click();
                        $(that.parent.config.shelf).children('ul').html('');
                        that.parent.data.shelfId = false;
                    }
                    app.helpers.computeWidth('shelf');
        			app.helpers.computeWidth('module');
        			app.triggerEvent('shelfsLoaded');
              //console.log("get ends");
            });

        },
        /**
         * Creates a JSON representation of a shelf and saves it.
         */
        save: function(){
            var cnf = this.parent.config;
            var mod = $(cnf.shelf);

            var json = {
                version: 1,
                meta: {
                    title: false
                },
                track0: []
            }
            if(($.trim($('#shelfTitle').val()) != '') ){
                $('#shelfId').attr('disabled', 'disabled');
            }
            if($('#shelfId').attr('disabled')) {
                json.meta.title = $.trim($('#shelfTitle').val());
            }else{
                json.meta.title = $('#shelfId :selected').html();
                var elems = mod.find('li').each( function(i) {
                    var details = Ing.findInDOM().data.map[$(this).attr('id')];
                    json.track0.push(parseInt(details.id));
                });

            }
            if (Ing.findInDOM().data.change)
            {
	            // json.meta.title = $('#shelfId :selected').html();
                var elems = mod.find('li').each( function(i) {
                    var details = Ing.findInDOM().data.map[$(this).attr('id')];
                    json.track0.push(parseInt(details.id));
                });
            }

            if(($.trim($('#shelfTitle').val()) != '')){
                $('#shelfTitle').val('');
                $('#shelfId').removeAttr('disabled');
                $(this.parent.config.shelf).children('ul').html('');
            }
            if(!json.meta.title){
                var d = new Date();
                var hlp = this.parent.helpers;
                var dateStr = d.getFullYear() + '-' + hlp.lz(d.getMonth() + 1) + '-' + hlp.lz(d.getDate()) + ' ' +
                                hlp.lz(d.getHours()) + ':' + hlp.lz(d.getMinutes());
                json.meta.title = t.COLLECTION_CREATED + ' ' + dateStr;
            }
            this.parent.callbacks.saveShelf(json);

            //console.log("save ends");
        },
        /**
         * Shows selected shelf
         */
        showShelf: function(shelfId){
            if(!shelfId){
                var json = this.parent.data.shelfs[0];
            }else{
                var json = false;
                $.each(this.parent.data.shelfs, function(){
                    if(json === false && this.meta.id == shelfId){
                        json = this;
                    }
                });
            }
            var id = this.parent.config.shelf;
            if(json.meta.id) {
                this.parent.data.shelfId = json.meta.id;
            }
            var root = $(this.parent.config.shelf).children('ul');
            var els = this.parent.elements;
            root.html('');
            for(var i = 0, len = json.track0.length; i < len; i++) {
                els.attach(new els.segment(json.track0[i]), root);
                $(id).css('width', parseInt($(id).css('width')) + this.parent.config.elemWrapperWidth + 10);
            }
            $('#shelfId option[value=' + shelfId + ']').attr('selected', 'selected');
            $('#shelfId').sb('refresh');
            $('#newCollection').hide();
            $('#collectionSelector').show();
            this.parent.data.shelfJSON = json;
            this.parent.helpers.cookie.set('ing_admin_lastShelf', shelfId);

            //console.log("showShelf ends");
        }
    },
    /**
     * Loads a filelist into a datastore according
     * to passed parameters and constraints. Creates a
     * roller style list or fills up already created list
     * with items.
     */
    this.loadFiles = function(append) {
        if(append == undefined) {
            append = true;
        }
        var url = null;
        if(typeof this.data.nextURL == 'undefined') {
            url = this.config.nextURL + "?my_files=1&from_my_groups=1"
        } else {
            url = this.data.nextURL;
        }
        var that = this;
        if(url) {
            if (!!document.getElementById('rollerWrapper')) {
            	app.helpers.throbber('#rollerWrapper');
            }
            $.get(
            url, function(data) {
                if(typeof data != 'object') { // IE bug --
                    data = $.parseJSON(data);
                }
                that.data.nextURL = data.meta['prev-page-url'] || false;
                that.data.totalPages = data.meta['total-pages'];
                var newFiles = data.entries;
                var els = that.elements;
                if(append) {
                    var iterator = that.data.files.length;
                    that.data.files = that.data.files.concat(newFiles);
                } else {
                    var iterator = 0;
                    that.data.files = newFiles;
                    that.roller.clear();
                }
                var ul = els.getObj(new els.list());
                var scr = that.roller.scr() || false;
                var item = false;
                for ( var i = 0, len = newFiles.length; i < len; i++ ) {
                    item = els.getObj(new els.fileItem(newFiles[i], i + iterator));
                    item.appendTo(ul);
                    // item.tooltip({
                     // effect: 'slide',
                     // slideOffset: -50
                     // });
                    that.roller.addDraggable(item);
                    if ( ((i % 8 == 0) && i) || i == len - 1 ) {
                        if(scr) {
                            scr.addItem(ul);
                        } else {
                            ul.appendTo($('#rollerItems'));
                        }
                        ul = els.getObj(new els.list());
                    }
                }
                if(newFiles.length > 0) {
                    $('#rollerWrapper .next').removeClass('disabled');
                }
                if(!append) {
                    scr.begin();
                    $(that.config.rollerNavi).html('');
                }

                var loop = data.meta['total-pages'] - $(that.config.rollerNavi).children('a').length;
                for(var i = 0; i < loop; i++) {
                    $(that.config.rollerNavi).append($('<a />').attr('id', i).addClass(!i ? 'active' : ''));
                }
                $(that.config.totalFilesCount).html(data.meta['total-entries']);
                if(!scr) {
                    that.roller.addScrollable();
                    that.loadFiles();
                }
                if (!!document.getElementById('rollerWrapper')) {
                	app.helpers.throbber('#rollerWrapper', 'remove');
                }
                if ($('#rollerItems li.active').length == 0) {
                    $('#rollerWrapper').trigger('loaded');                	
                }
            });

            //console.log("get2 ends");
        }
    },
    /**
     * Admin's dashboard widgets.
     * Each widget's constructor should provide a
     * HTML wrapper ID, in order to bind widget instance
     * with a HTML wrapper.
     * Each widget should provide an init function, that is
     * being called upon widget instantiation.
     */
    this.widgets = {
        'ldap': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/ldap-config/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.LDAP_USE + ':</dt><dd>' + (data.use_ldap  == '1' ? t.TRUE.toLowerCase() : t.FALSE.toLowerCase()) + '</dd>');
                        root.append('<dt>' + t.LDAP_URL + ':</dt><dd>' + data.ldap_url + '</dd>');
                        root.append('<dt>' + t.LDAP_GROUPS_DN + ':</dt><dd>' + data.groups_dn + '</dd>');
                        root.append('<dt>' + t.LDAP_GROUP_TYPE + ':</dt><dd>' + data.group_type + '</dd>');
                        root.append('<dt>' + t.LDAP_USERS_DN + ':</dt><dd>' + data.users_dn + '</dd>');
                        root.append('<dt>' + t.LDAP_USER_DISCR + ':</dt><dd>' + data.user_discriminant + '</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'my_content_stats': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/mycontent/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.TOTAL_CONTENT + ':</dt><dd>' + data.total + '</dd>');
                        root.append('<dt>' + t.VIDEO + ':</dt><dd>' + data.video + '</dd>');
                        root.append('<dt>' + t.AUDIO + ':</dt><dd>' + data.audio + '</dd>');
                        root.append('<dt>' + t.IMAGE + ':</dt><dd>' + data.image + '</dd>');
                        root.append('<dt>' + t.TEXT + ':</dt><dd>' + data.text + '</dd>');
                        root.append('<dt>' + t.SLIDES + ':</dt><dd>' + data.slides + '</dd>');
                        root.append('<dt>' + t.SCORM + ':</dt><dd>' + data.scorm + '</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'my_groups_stats': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/mygroups/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.NUMBER_OF_MY_GROUPS + ':</dt><dd>' + data.total + ' ('+data.my_managed_groups+' '+ t.MANAGED +')</dd>');
                        root.append('<dt>' + t.NUMBER_OF_USERS_IN_MY_GROUPS + ':</dt><dd>' + data.users_in_my_groups + ' ('+data.unique_users_in_my_groups+' '+t.UNIQUE +')</dd>');
                        root.append('<dt>' + t.NUMBER_OF_USERS_IN_MY_MANAGE_GROUPS + ':</dt><dd>' + data.users_in_my_managed_groups + ' ('+data.unique_users_in_my_managed_groups+' '+ t.UNIQUE +')</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'my_reports_stats': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/myreports/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.TOTAL_REPORTS + ':</dt><dd>' + data.total + '</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'my_modules_stats': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/mymodules/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.TOTAL_MODULES + ':</dt><dd>' + data.total + '</dd>');
                        root.append('<dt>' + t.DRAFTS + ':</dt><dd>' + data.drafts + '</dd>');
                        root.append('<dt>' + t.ACTIVE + ':</dt><dd>' + data.active + '</dd>');
                        root.append('<dt>' + t.DEACTIVATED + ':</dt><dd>' + data.deactivated + '</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'my_templates_stats': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/mytemplates/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.append('<dt>' + t.TOTAL_NUMBER_OF_TEMPLATES + ':</dt><dd>' + data.total + '</dd>');
//                        root.append('<dt>' + t.TOTAL_MODULES + ':</dt><dd>' + data.total + '</dd>');
//                        root.append('<dt>' + t.DRAFTS + ':</dt><dd>' + data.drafts + '</dd>');
//                        root.append('<dt>' + t.ACTIVE + ':</dt><dd>' + data.active + '</dd>');
//                        root.append('<dt>' + t.DEACTIVATED + ':</dt><dd>' + data.deactivated + '</dd>');
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        },
        'administrative_tools': function(id){
            this.id = '#' + id;
            this.init = function(){
                var ing = Ing.findInDOM();
                var that = this;
                ing.helpers.throbber(this.id);
                $.get(
                    '/administration/tools/',
                    function(data){
                        var root = $(that.id + ' .content dl');
                        root.find('dd#qualityOfContent').text(data.quality_of_content);
                        root.find('dd#useDms').text(data.use_dms);
                        root.find('dd#useLdap').text(data.use_ldap);
                        root.find('dd#mappedGroups').text(data.mapped_groups);
                        ing.helpers.throbber(that.id, 'remove');
                });
            }
        }
    }
    /**
     * Temporary functions -- should be overwritten
     */
    this.addInterfaces = function(obj) {
        obj.resizable({
            grid: 139,
            handles: 'w,e',
            'minWidth': 139,
            stop: function(event, ui) {
                Ing.findInDOM().module.snapBackOnOverlap(event, ui, this);
                app.triggerEvent('itemChanged', ['sound']);
            },
            containment: 'parent'
        });
        if(!(obj.is(".ui-draggable"))) {
            obj.draggable({
                grid: [139, 0],
                axis: 'x',
                start: function(event, ui) {
                    Ing.findInDOM().data.temporaryDrag = ui.helper.css('left');
                },
                stop: function(event, ui) {
                    Ing.findInDOM().module.snapBackOnOverlap(event, ui, this);
                    app.triggerEvent('itemChanged', ['sound']);
                }
            });
        }
    },
    /**
     * A patch for default jQuery event triggering.
     * Populates events into the app and enables handling
     * events called from outside the app by app's event
     * handling functions.
     */
    this.triggerEvent = function(event, args) {
        $(this).trigger(event, args);
    }
};
