function MediaPlayer(spawner) {
	var me = this;
	
	me.playerConfig = app.config.player;
    me.parent = spawner;
    me.playlistParams = "";
    me.playerSize = "";
    me.playlist = "";
    me.domInstance = "";
    me.trackUser = true;
    me.currentState = {};
    me.controlsTimer = 0;
    me.selectedSource = 0;
    me.preventBtnControl = false;
    me.sourceSet = [];
    me.backgroundAudio = {currentPlay: false, tracks: []};
    me.backgroundPlayer = false;
    
    /**
     * Player API.
     *
     * API consists of two groups of functions.
     * One group controls flash player using JS.
     * The other group is used to receive callbacks
     * from the player.
     *
     * @todo: Move the old api here.
     */
    me.api = {
        /**
         * Object holding handler functions
         */
        handlers: {
        	info: 'app.callbacks.mp.info_handler',
        	error: 'app.callbacks.mp.error_handler',
        	exception: 'app.callbacks.mp.exception_handler',
        	keypress: 'app.callbacks.mp.keypress_handler',
        	defaultClick: 'app.callbacks.mp.pdf_handler',
        	setActive: 'app.callbacks.mp.activeItem_handler',
        	thisIsFinished: 'app.callbacks.mp.this_is_finished',
        	showPDF: 'app.callbacks.mp.pdf_handler',
        	showSCORM: 'app.callbacks.mp.scorm_handler',
        	showHTML: 'app.callbacks.mp.html_handler',
        	showPPT: 'app.callbacks.mp.pdf_handler',
        	showDOC: 'app.callbacks.mp.pdf_handler',
        	showText: 'app.callbacks.mp.html_handler',
        	goTo: 'app.player.switchSource',
        	play: 'app.player.statusHandler',
        	pause: 'app.player.statusHandler',
        	seeked: 'app.player.statusHandler',
        	ended: 'app.player.statusHandler',
        	durationchange: 'app.player.updateDuration',
        	loadedmetadata: 'app.player.updateDuration',
        	timeupdate: 'app.player.updateCurrentTime',
        	segmentCompleted: 'app.player.handleCompleted',
        	mousemove: 'app.player.handleMousemove',
        	touchstart: 'app.player.handleMousemove',
        	touchend: 'app.player.handleMousemove',
        	touchmove: 'app.player.handleMousemove',
        	onscreenrotate: 'app.player.handleRotation'
        },
        /**
         * Holds module player events 
         * appearing across every player 
         */
        events: [
        	'info',
        	'error',
        	'exception',
        	'keypress',
        	'defaultClick',
        	'setActive',
        	'thisIsFinished',
        	'segmentCompleted',
        	'showPDF',
        	'showSCORM',
        	'showHTML',
        	'showPPT',
        	'showDOC',
        	'showText',
        	'mousemove',
        	'onscreenrotate',
        	'goTo'
        ],
        /**
         * Holds video/audio player events
         */
        mediaEvents: [
         	'play',
         	'pause',
         	'seeked',
         	'ended',
         	'durationchange',
         	'loadedmetadata',
         	'timeupdate',
         	'volumechange',
         	'waiting',
         	'canplaythrough',
         	'stalled',
         	'error'
        ],
        /**
         * Registering action handler
         */
        register: function(name, type) {
            this.handlers[type] = name;
            return true;
        },
        /**
         * Unregistering action handler
         */
        unregister: function(type) {
            delete this.handlers[type];
        },
        /**
         * Retrieving action handler of agiven type.
         *
         * Note: This function is used by a flash player
         * to get a proper function assigned to
         * a specified event.
         */
        get: function(type) {
            if(this.handlers[type]) return this.handlers[type];
            return false;
        },
        /**
         * Calls proper handler for given event 
         * and passes proper scope to this handler
         */
        callHandler: function(handler, params) {
        	var nodes = this.get(handler),
        		func = me.parent,
        		scope;

        	if (!nodes) return false;

        	nodes = nodes.split('.').slice(1);
        	$.each(nodes, function(index){
        		scope = func;
        		func = func[nodes[index]];
        	});
        	func.apply(scope, params);
        },
        /**
         * Starts playback from a given index
         */
        play: function(i) {
        	if (i != undefined) {
	        	if (me.playerConfig.mode == "html5") {
	        		$('#video').trigger('goTo', [i]);
	        	} else {
	        		if ($('#flashCustomMsg').length){
	        			$('#flashCustomMsg').remove();
		        		$('.goBack').remove();
	        		}
	        		document.getElementById('video').goTo(i + 1);
	        	}
        	} else if (!!me.domInstance.paused) {
        		this.resume();
        	}
        },
        /**
         * Calls player pause function
         */
        pause: function() {
        	if (me.domInstance && !!!me.domInstance.paused) me.domInstance.pause();
        },
        /**
         * Calls player playe/resume funcion 
         * depending if it's html5 or flash player
         */
        resume: function(){
        	if (me.domInstance && me.playerConfig.mode == "html5") {
        		me.domInstance.play();
        	} else if (me.domInstance) {
        		me.domInstance.resume();
        	}      	
        },
        /**
         * Checks player state and calls play 
         * or pause depending on player state
         */
        togglePlay: function() {
    		if (!!me.domInstance.paused) {
    			me.domInstance.play();
    		} else if (!!me.domInstance) {
    			me.domInstance.pause();
    		}
        }
    },
    /**
     * Initializing. Binds player displaying functionality
     * to a splash. Displays the player using nyroModal window.
     */
    me.init = function() {
        var appConfig = me.parent.config,
        	playerObj,
        	obj,
        	parent = me.parent
        	playerId = (me.playerConfig.mode == 'html5') ? "video": "mplayer" ;
        
    	if (me.playerConfig.mode == "html5" && me.playerConfig.html5player.touch_support)
    		me.api.events = me.api.events.concat(['touchstart', 'touchend', 'touchmove']);
        
        $(appConfig.player.splash).live('click', function(event) {
        	me.trackUser = false;
        	event.preventDefault();
        	obj = parent.data.files[parent.helpers.find($(appConfig.fileId).html())];
        	playerObj = $('<div class="mplayerWrapper"><a href="javascript:void(0);" class="closeFW oneElement"></a><div id="' + playerId + '"></div></div>');
        	me.playModal(obj, playerObj, 'transparent');
        	if (me.playerConfig.mode == 'html5') {
            	me.adjustControls();
            	if (app.data.filetypes[obj.type] != "video" && app.data.filetypes[obj.type] != "music") 
            		$('#mediaControls').toggleClass('disabled', true);
            	if (app.data.filetypes[obj.type] != "image") 
            		$('#imageControls').toggleClass('disabled', true);
            	$('#video').on('mousemove', me.handleMousemove);
            	$(me.domInstance).on(me.api.mediaEvents.join(' '), me.mediaEventsHandler);
        	}
            return false;
        });
    };
    
    /**
     * Method responsible for embedding 
     * flash player object with specified params
     */
    me.spawnFlash = function(mediaType, playerSize, flashVars, windowMode){
    	var appConfig = me.parent.config,
    		params = appConfig.player.flashPlayer.params;
    	
    	params.wmode = windowMode;
		swfobject.embedSWF(
			appConfig.mediaURL + appConfig.player.flashPlayer.url,
			mediaType,
			playerSize.width,
			playerSize.height,
			appConfig.player.minFlashVersion,
			false,
			flashVars,
			params,{}
		);
    };
    
    /**
     * Method responsible for embedding HTML5 player.
     * Method checks if player should be called in playlist mode
     * or if it's only called for single file
     */
    me.spawnHTML5 = function(playerSize, params, windowMode){
    	var sourceUrl = params.contentURL;
    	
    	$('#video').unbind();
    	if (params.cType == "playlist") {
            $.get(decodeURIComponent(sourceUrl), function(data) {
            	me.playlist = data.track0;
            	me.backgroundAudio.tracks = data.track1;
            	me.playlistParams = data.meta;
            	me.playlistParams['playingIndex'] = parseInt(params.playingIndex); 
            	me.initPlayback(playerSize, params, windowMode)
            });
    	} else {
        	me.appendControls(document.getElementById('video'));
    		sourceUrl = decodeURIComponent(sourceUrl.substring(0,sourceUrl.lastIndexOf(".")));
    		me.domInstance = me.callForPlayer(document.getElementById('video'), sourceUrl, params);
    		if (me.domInstance) {
    			me.domInstance.setAttribute('width', playerSize.width);
    			me.domInstance.setAttribute('height', playerSize.height);
    			$('#video').addClass(params.cType == "music" ? 'music': 'default');
    			me.domInstance.play();
    		}
    	}
    };
    
    /**
     * Playback initialization. This method sets
     * proper player params and event listeners
     * specified for playlist mode. 
     */
    me.initPlayback = function(playerSize, params, windowMode) {
    	var moduleElements = $(me.parent.config.module).find('li'),
    		playerConfig = me.parent.config.player.html5player;
    	me.playerSize = playerSize;
    	$('#video').css('text-align', 'center');
    	me.appendControls(document.getElementById('video'));
    	$('#video').on(me.api.events.join(' '), function(event, data){
    		me.api.callHandler(event.type, [data], app.callbacks.mp);
    	});
    	if (!!me.trackUser) $('#video').on('onstateChange', function(){
	    		$('#video').trigger('info', [JSON.stringify(me.currentState)]);
	    	});
    	
    	if (!!me.backgroundAudio.tracks.length) me.spawnBackgroundAudio();
    	
        if (moduleElements.length > 0) {
        	moduleElements.each( function(i) {
	            if (i == params.playingIndex) {
	                $(this).addClass('current');
	                $('#video').trigger('goTo', [i]);
	            } else {
	                $(this).removeClass('current');
	            }
	        });
        	if (playerConfig.touch_support || !playerConfig.fullscreen_support)
        		me.enterFullScreen(document.getElementById('video'));
        } else {
            $('#video').trigger('goTo', [params.playingIndex]); 
        }
    };
    
    /**
     * Background sound initialization. This method sets
     * proper background audio player params and event listeners.
     * Will be called only when player is in playlist mode.
     */
    me.spawnBackgroundAudio = function() {
    	me.backgroundPlayer = document.createElement('audio');
    	me.backgroundPlayer.setAttribute('id', 'backgroundAudio');
    	document.getElementById('video').appendChild(me.backgroundPlayer);
    	me.backgroundPlayer.src = '';
    	$(me.backgroundPlayer).unbind();
    	$(me.backgroundPlayer).on('ended', function(event){
    		event.preventDefault();
    		if (me.backgroundAudio.currentPlay === false || me.backgroundAudio.tracks.length < me.backgroundAudio.currentPlay + 1) return;
    		if (me.backgroundAudio.tracks[me.backgroundAudio.currentPlay].playback_mode == "repeat") me.backgroundPlayer.play();
    		return;
    	});
    };

    /**
     * Decision logic responsible for changing 
     * background sound sources depending
     * on currently played lesson segment.
     */
    me.backgroundSourceHandler = function(index) {
    	var bgTracks = me.backgroundAudio.tracks,
    		playing = me.backgroundAudio.currentPlay;
    	
		for (var i = 0, len = bgTracks.length; i < len; i++) {
			if (playing !== i && bgTracks[i].start <= index && index <= bgTracks[i].end) {
				var url =  decodeURIComponent(bgTracks[i].url.substring(0,bgTracks[i].url.lastIndexOf(".")));
				if (!me.backgroundPlayer.paused)
					me.backgroundPlayer.pause();
				me.backgroundPlayer.src = me.pickAudioFormats(me.parent.config, url)[0].src;
				me.backgroundAudio.currentPlay = i;
				me.backgroundPlayer.play();
				return;
			}
		}
		if (playing !== false && bgTracks.length && (bgTracks[playing].start > index || index > bgTracks[playing].end)) {
			me.backgroundPlayer.pause();
		} else if(playing == false) {
			me.backgroundPlayer.play();
		}
    };
    
    /**
     * When player is in playlist mode, this method 
     * is responsible for switching between different 
     * sources and internal players e.g. choosing 
     * between video/audio.document players.
     */
    me.switchSource = function(index) {
		var appConfig = me.parent.config,
			playEntry = me.playlist[index],
			sourceUrl = (!!playEntry) ? decodeURIComponent(playEntry.url.substring(0,playEntry.url.lastIndexOf("."))): false,
			mplayerWrapper = document.getElementById('video');
			
		me.bindPrevNextEvents();
		if (playEntry === undefined) { playEntry = {}; }
		if ($('.playerHTML5').length) { $('.playerHTML5').parent().remove(); }
		if (!sourceUrl && !playEntry.hasOwnProperty('type')) {
			if (!!me.backgroundPlayer) me.backgroundPlayer.pause();
			if (me.isFullScreen())
				me.exitFullScreen();
			playEntry = {cType: 'finish'};
			me.playlistParams.playingIndex = index;
			me.changeState({'event_type': 'END', 'segment_id': me.currentState.segment_id});
		} else {
			if (!!me.backgroundPlayer) me.backgroundSourceHandler(index);
			$('.goodbyeMsg').remove();
			playEntry.cType = app.data.filetypes[playEntry.type];
			playEntry.contentURL = playEntry.url;
			me.selectedSource = 0;
		}
		
		if (!!document.getElementById('mplayer')) {
			if (!!me.currentState.segment_id) {
				me.changeState({'event_type': 'LEAVING', 'segment_id':  me.currentState.segment_id});				
			}
			me.clearEvents();
			$('#mplayer').remove();
		}
		if ($('#video').hasClass('fullscreen')) {
			$('#video').attr('class', 'fullscreen');
		} else $('#video').removeClass();
		
		$('#mediaLoader').hide();
		$('#video .msgContainer').hide();
		$('#imageControls').toggleClass('disabled', true);
		if (me.trackUser) $('#video').trigger('setActive', [index]);
		me.playlistParams.playingIndex = index;
		me.domInstance = me.callForPlayer(mplayerWrapper, sourceUrl, playEntry);
		if (me.domInstance) {
			$('#video').css('background-image', 'none');
			me.domInstance.setAttribute('id', 'mplayer');
			me.domInstance.setAttribute('max-height', me.playerSize.height);
    		me.changeState({'event_type': 'START', 'segment_id': playEntry.segment_id});
        	$(me.domInstance).on(me.api.mediaEvents.join(' '), me.mediaEventsHandler);
        	$('#mediaControls').toggleClass('disabled', false);
        	$('#playButton_bigGray').show();
        	me.preventBtnControl = false;
        	me.domInstance.play();
		} else {
			$('#mediaControls').toggleClass('disabled', true);
			$('.setFullscreen').toggleClass('on', me.isFullScreen());
//			if (!!playEntry.preview_url) $('#video').css('background-image', 'url(' + playEntry.preview_url +')');
		}
		$('#video').addClass(playEntry.cType);
		me.adjustControls();
		if (playEntry.cType == 'image') {
    		me.changeState({'event_type': 'END', 'segment_id': playEntry.segment_id});
		}
    };
    
    /**
     * Method responsible for decision which internal player
     * should be selected for specified source.
     */
    me.callForPlayer = function(mplayerWrapper, sourceUrl, params) {
    	var appConfig = me.parent.config,
			mplayer;

    	if(params.cType == "video") {
    		mplayer = document.createElement('video');
	    	mplayer.setAttribute('preload', 'metadata');
    		me.sourceSet = me.pickVideoFormats(appConfig, sourceUrl);
    		mplayer.setAttribute('src', me.sourceSet[0].src);
    		mplayerWrapper.appendChild(mplayer);
    		mplayer.load();
    	} else if (params.cType == "music") {
    		mplayer = document.createElement('audio');
	    	mplayer.setAttribute('preload', 'metadata');
	    	me.sourceSet = me.pickAudioFormats(appConfig, sourceUrl);
    		mplayer.setAttribute('src', me.sourceSet[0].src);
    		mplayerWrapper.appendChild(mplayer);
    		mplayer.load();
    	} else if (params.cType == "image") {
    		me.changeState({'event_type': 'START', 'segment_id': params.segment_id});
    		$('#imageControls').toggleClass('disabled', false);
			mplayer = document.createElement('div');
			mplayer.setAttribute('id', 'mplayer');
			var playerImage = document.createElement('img');
			playerImage.src = (!!params.url) ? params.url: decodeURIComponent(params.contentURL);
			playerImage.onload = function() {
    			$('#video').css('background-image', 'none');
    			playerImage.dimentions = { width: (!!playerImage.naturalWidth) ? playerImage.naturalWidth: playerImage.width,
    								       height: (!!playerImage.naturalHeight) ? playerImage.naturalHeight: playerImage.height};
    			playerImage.setAttribute('maxWidth', playerImage.dimentions.width);
    			playerImage.setAttribute('maxHeight', playerImage.dimentions.height);
    			playerImage.setAttribute('class', 'imagePlayer');
    			if (playerImage.dimentions.height < $('#mplayer').height())
    				$(playerImage).height(playerImage.dimentions.height);
    			$(playerImage).css('top', ($('#mplayer').innerHeight() - $(playerImage).height())/2)	
    		}
			mplayerWrapper.appendChild(mplayer);
			mplayer.appendChild(playerImage);
			
    		return false;
    	} else {
        	if (params.cType == 'finish') {
        		me.preventBtnControl = false;
        		$('#video').css('background-image', 'none');
        		goodbyeMsg = document.createElement('div');
        		goodbyeMsg.setAttribute('class', 'goodbyeMsg');
        		var msgBody = '<div class="messageBody">'; 
        		msgBody += (!!me.playlistParams.completion_msg)? app.helpers.htmlSpecialDecoder(me.playlistParams.completion_msg): t.LESSON_FINISHED;
        		msgBody += '</div>';
        		mplayerWrapper.appendChild(goodbyeMsg);
        		$(goodbyeMsg).html($(msgBody));
        		$(goodbyeMsg).css('top', ($('#video').height() - $(goodbyeMsg).find('.messageBody').outerHeight())/2);
        	} else {
        		me.preventBtnControl = true;
        		me.currentState = {'event_type': 'START', 'segment_id': params.segment_id}
        		me.callExternalPlayer(params);
        	}
    		return false;
    	}
    	return mplayer;
    };
    
    /**
     * Method responsible for checking which video formats
     * browser support and picking proper file formats order.
     */
    me.pickVideoFormats = function(appConfig, sourceUrl) {
    	var supportedFormats = new Array();
    	
    	supportedFormats.push({format: 'mp4', support: appConfig.player.html5player.mp4_support,
    						 src: sourceUrl + '.mp4'},
							{format: 'webm', support: appConfig.player.html5player.webM_support,
    						 src: sourceUrl + '.webm'},
							{format: 'ogv', support: appConfig.player.html5player.theora_support,
    						 src: sourceUrl + '.ogv'});
    	
    	supportedFormats = $.grep(supportedFormats, function(format) {
    		return !!format.support;
    	});
    	
    	supportedFormats.sort(function(a,b) {
    		return (((b.support == "probably")? 1: 0) - ((a.support == "probably")? 1: 0));
    	});
    	
    	return supportedFormats;
    };

    /**
     * Method responsible for checking which audio formats
     * browser support and picking proper file formats order.
     */
    me.pickAudioFormats = function(appConfig, sourceUrl) {
    	var supportedFormats = new Array();
    	
    	supportedFormats.push({format: 'ogg', support: appConfig.player.html5player.ogg_support,
    						 src: sourceUrl + '.ogg'},
							{format: 'mp3', support: appConfig.player.html5player.mp3_support,
    						 src: sourceUrl + '.mp3'});
    	
    	supportedFormats = $.grep(supportedFormats, function(format) {
    		return !!format.support;
    	});
    	
    	supportedFormats.sort(function(a,b) {
    		return (((b.support == "probably")? 1: 0) - ((a.support == "probably")? 1: 0));
    	});
    	
    	return supportedFormats;
    };
    
    /**
     * Generates <source> tags for audio/video players.
     * This method is currently disabled and source
     * is set directly as video/audio attribute.
     */
    me.generateSourceTags = function (targetPlayer, mediaFormats, sourceUrl) {
    	var generatedSource;
    	
    	$.each(mediaFormats, function() {
    		generatedSource = document.createElement('source');
    		generatedSource.setAttribute('id', this.format);
    		generatedSource.setAttribute('src', sourceUrl + '.' + this.format);
    		targetPlayer.appendChild(generatedSource);
    	});
    };
    
    /**
     * Creates all possible cotrols which 
     * will be requred accross different players, 
     * and binds proper event listeners for them.
     */
    me.appendControls = function(playerContainer) {
    	var playerNext = document.createElement('div'),
    		playerPrev = document.createElement('div'),
    		mediaControls = document.createElement('div'),
    		imageControls = document.createElement('div'),
    		mediaLoader = document.createElement('div'),
    		msgContainer = document.createElement('div'),
    		bigPlay = document.createElement('div'),
    		controlsBody;
    	
    	playerNext.setAttribute('class', 'goAhead');
    	playerPrev.setAttribute('class', 'goBack');
    	playerNext.setAttribute('id', 'goAhead');
    	playerPrev.setAttribute('id', 'goBack');
    	mediaControls.setAttribute('id', 'mediaControls');
    	imageControls.setAttribute('id', 'imageControls');
    	mediaLoader.setAttribute('id', 'mediaLoader');
    	msgContainer.setAttribute('class', 'msgContainer');
    	bigPlay.setAttribute('id', 'playButton_bigGray');
    	bigPlay.appendChild(document.createElement('div'));
    	mediaLoader.innerHTML = "<div>" + t.PLAYER_BUFFERING + "</div>";
    	
    	playerContainer.appendChild(playerNext);
    	playerContainer.appendChild(playerPrev);
    	playerContainer.appendChild(mediaControls);
    	playerContainer.appendChild(imageControls);
    	playerContainer.appendChild(mediaLoader);
    	playerContainer.appendChild(bigPlay);
    	playerContainer.appendChild(msgContainer);
    	
    	$('#video .msgContainer').html('<div><span class="msgHeader">' + 
				 t.ERROR_OCURRED_WITHOUT_DOT + '</span><span class="msgBody"></span></div>')
    	
    	controlsBody = '<div id="playerBtnPlay"></div><div class="playerProgress">' +
    				'<div id="playerSeekHandle"></div><div class="progressBg"></div></div><div id="playerRightControls">' +
    					'<span class="currentTime">0:00</span><span>/</span><span class="mediaDuration">0:00</span>';
    	controlsBody += '<div class="setFullscreen"></div><div class="volumeHandle"></div></div>';
    	
    	$(mediaControls).html(controlsBody);
    	$(imageControls).html('<div class="setOriginal"></div>');
    	
    	$(bigPlay).on('click', function(event){
    		event.preventDefault();
    		me.api.togglePlay();
    	});
    	
    	$(imageControls).append('<div class="setFullscreen"></div>');
    	
    	me.bindPrevNextEvents();
    	$('#playerBtnPlay').on('click', function(event){
    		event.preventDefault();
    		me.api.togglePlay();
    	});
    	$('#mediaControls .playerProgress').on('click', function(event){
    		event.preventDefault();
    		var goTo = event.clientX - $('#mediaControls .playerProgress').offset().left
    		var goTo = goTo / $('#mediaControls .playerProgress').width() * me.domInstance.duration;
    		me.seekPosition(goTo);
    	});
    	$('#mediaControls .volumeHandle').on('click', function(event){
    		event.preventDefault();
    		me.domInstance.volume = (me.domInstance.volume == 1) ? 0: 1;
    	});
    	$('#imageControls .setOriginal').on('click', function(event){
    		event.preventDefault();
    		$('#mplayer .imagePlayer').toggleClass('original');
    		$('#imageControls .setOriginal').toggleClass('on');
    	});
		$('#video').on('click', '.setFullscreen', me.fullscreenHandle);
		$(document).on('webkitfullscreenchange mozfullscreenchange fullscreenchange', function(event) {
			$('.setFullscreen').toggleClass('on', me.isFullScreen());
			if (event.type != "fullscreenchange"){
		    	var delayResize = setTimeout(function(){
		    		clearTimeout(delayResize);
		    		me.recalculateHtmlPlayer();
		    	}, 300);
			} else {
				me.recalculateHtmlPlayer();		
//				window.scrollTo(0,0);
			}
		});
    };
    
    /**
     * Handles specific controls appearance.
     * For example checks if nex item can be played
     * and next button should be displayed.
     */
    me.adjustControls = function() {
    	var itemsToPlay = me.playlist.length,
    		canPlayNext = $('#moduleList').find('li');
    	
    	if (me.playlistParams.playingIndex + 1 <= me.playlist.length) {
    		canPlayNext = $(canPlayNext[me.playlistParams.playingIndex + 1]).find('.courseApla').length < 1
    					|| me.playlist[me.playlistParams.playingIndex + 1].allow_skipping
    					|| me.playlist[me.playlist.length -1].is_learnt;
    	} else canPlayNext = (me.playlist.length < 0 || me.playlistParams.playingIndex <= me.playlist.length);

		$('#playerSeekHandle').css('left', "0");
		$('#mediaControls .progressBg').css('width', '0');
		$(me.domInstance).trigger('durationchange');
		$('#mediaControls .volumeHandle').toggleClass('off', false);
    	$('#playerBtnPlay').toggleClass('pause', false);
    	if(!me.preventBtnControl) {
    		$('#video .goBack').toggleClass('disabled', ((!me.playlistParams || itemsToPlay == 1 || me.playlistParams.playingIndex == 0)
					&& (me.playlistParams.playingIndex != itemsToPlay || itemsToPlay == 0 )));

			$('#video .goAhead').toggleClass('disabled', (!me.playlistParams || itemsToPlay <= 1
								|| !!(document.getElementById('moduleList') && !canPlayNext)
								|| me.playlistParams.playingIndex + 1 >= itemsToPlay));    		
    	}
    };  
    
    me.bindPrevNextEvents = function() {
    	if (document.getElementById('goBack').hasEventListener('click') == false){
        	$('.goBack').on('click', function(event){
        		event.preventDefault();
        		$('#video').trigger('goTo', [me.playlistParams.playingIndex - 1]);
        	});
    	}
    	if (document.getElementById('goAhead').hasEventListener('click') == false){
	    	$('.goAhead').on('click', function(event){
	    		event.preventDefault();
	    		$('#video').trigger('goTo', [me.playlistParams.playingIndex + 1]);
	    	});
    	}
    };
    
    me.unbindPrevNextEvents = function() {
    	$('.goAhead').unbind('click');
    	$('.goBack').unbind('click');
    };
    
    /**
     * This method handles controls hiding
     * after specified time when mouse is inactive.
     */
    me.handleMousemove = function(event) {
    	$('#video').toggleClass('active', true);
    	clearTimeout(me.controlsTimer);
    	me.controlsTimer = setTimeout(function(){
        	$('#video').toggleClass('active', false);
    	}, 2000);
    };

    /**
     * Basic handler for all media events.
     * This handler prepares initial data
     * for real event handlers.
     */
    me.mediaEventsHandler = function(event, data){
    	var params = [];
    	switch(event.type) {
    		case 'volumechange':
    			$('#mediaControls .volumeHandle').toggleClass('off', !!!me.domInstance.volume);
    			return
    		case "canplaythrough":
    			$('#mediaLoader').hide();
    			return
    		case 'waiting':
    			if ($('#playButton_bigGray').is(':visible')) {
    	    		$('#playButton_bigGray').hide();
    			}
    			if (!me.domInstance.ended) $('#mediaLoader').show();
    			return
    		case 'ended':
    			$('#mediaLoader').hide();
    			params.push('END');
    			break;
    		case 'seeked':
    			params.push('seek: ' + me.domInstance.currentTime + '!');
    			break;
    		case 'play':
    			if ($('#playButton_bigGray').is(':visible')) {
    	    		$('#playButton_bigGray').hide();
    			}
        		$('#playerBtnPlay').toggleClass('pause', true);
        		params.push('resume!');
        		break;
    		case 'pause':
        		$('#playerBtnPlay').toggleClass('pause', false);
        		params.push('pause!');
        		break;
    		case 'error':
    			me.handleError(event);
    			return
    	}
    	me.api.callHandler(event.type, params);
	};
	
    /**
     * Changes player state and triggers proper event.
     */
    me.changeState = function(state) {
    	me.currentState = state;

    	if (state.event_type == "END" && me.playlistParams.playingIndex == me.playlist.length -1) me.handleCompleted();
    	if (!!me.trackUser) $('#video').trigger('onstateChange');    		
    };

    /**
     * Unbinds all events from player
     */
    me.clearEvents = function() {
        $(me.domInstance).unbind();
    };
	
    /**
     * Handles specific playlist segment statuses
     */
    me.statusHandler = function(state) {
    	var msg = {'event_type': '', 'segment_id':  me.currentState.segment_id};
    	
    	if (state == "END" && me.playlistParams.playingIndex == me.playlist.length -1) me.handleCompleted();
    	if (state == "resume!" && !!me.domInstance.played && me.domInstance.played.length == 0) return;
    	msg.event_type = state;
    	me.changeState(msg);
    };
    
    /**
     * Method responsible for checking if next 
     * playlist item is available for playing.
     * This method also hides or shows 'next' button.
     */
    me.handleCompleted = function() {
    	var canPlayNext = $('#moduleList').find('li');

    	if (canPlayNext.length >= me.playlistParams.playingIndex + 1) {
    		canPlayNext = $(canPlayNext[me.playlistParams.playingIndex + 1]).find('.courseApla').length < 1
    					|| me.playlist[me.playlistParams.playingIndex + 1].allow_skipping
    					|| me.playlist[me.playlist.length -1].is_learnt;
    	} else canPlayNext = (me.playlistParams.playingIndex < me.playlist.length);
		$('#video .goAhead').toggleClass('disabled', !canPlayNext);   	
    };
    
    /**
     * Handler for audio/video players errors.
     */
    me.handleError = function(event) {
    	var error = event.target.error;
    	
    	if (!!!error) return;
    	
    	if (me.domInstance.networkState != me.domInstance.NETWORK_EMPTY){
	    	if (error.code == error.MEDIA_ERR_NETWORK) {
	         	$('#video .msgBody').html(t.ERROR_NETWORK);
	        	$('#mediaLoader').hide();
	        	$('#video .msgContainer').show();
	     	} else if (error.code == error.MEDIA_ERR_SRC_NOT_SUPPORTED
	    			|| me.domInstance.networkState == me.domInstance.NETWORK_NO_SOURCE) {
	    		if (!me.tryNextSource()) {
	    			$('#video .msgBody').html(t.ERROR_NOT_SUPORTED)
	    	    	$('#mediaLoader').hide();
	    	    	$('#video .msgContainer').show();
	    		};
	    	}
    	}
    };
    
    /**
     * Checks if another source is available for current item
	 * and if it is, then switches to it.
     */
    me.tryNextSource = function() {
    	if (me.selectedSource < me.sourceSet.length - 1) {
    		me.selectedSource++;
    		me.domInstance.src = me.sourceSet[me.selectedSource].src;
    		me.domInstance.load();
    		me.domInstance.play();
    		return true;
    	}
    };
    
    /**
     * Calls external player which is not 
     * one of html5 players: audio/video/image.
     */    
    me.callExternalPlayer = function(params) {
    	params.contentURL = decodeURIComponent(params.contentURL);
    	var cases = {
    		scorm: 'showSCORM',
    		pdf: 'showPDF',
    		html: 'showHTML',
    		text: 'showText',
    		doc: 'showDOC',
    		ppt: 'showPPT'
    	};
    	me.unbindPrevNextEvents();
    	if (params.cType == "pdf" || "doc" || "ppt") {
    		me.api.callHandler(cases[params.cType], [params.contentURL, params.pages_num]);
    	} else {
    		me.api.callHandler(cases[params.cType], [params.contentURL]);
    	}
    };
    
    /**
     * Method reponsible for handling audio/video progress.
     * Updates media played time and slider position.
     */
    me.updateCurrentTime = function() {
    	var secs = Math.round(me.domInstance.currentTime % 60),
    		mins = Math.floor(me.domInstance.currentTime / 60),
    		currentTime;
    	if (secs < 10) secs = "0" + secs;
    	currentTime = [mins, secs].join(":");
    	if ($('#playerRightControls .currentTime').html() != currentTime) {
    		$('#playerRightControls .currentTime').html(currentTime);
    		currentTime = Math.ceil(me.domInstance.currentTime / me.domInstance.duration * 100);
    		$('#playerSeekHandle').css('left', currentTime + "%");
    		$('#mediaControls .progressBg').css('width', currentTime + "%");
    	}
    };
    
    /**
     * Method reponsible for updating audio/video duration time.
     */    
    me.updateDuration = function() {
    	var secs = (parseInt(me.domInstance.duration) > 0) ? Math.round(me.domInstance.duration % 60) : 0,
    		mins = (parseInt(me.domInstance.duration) > 0) ? Math.floor(me.domInstance.duration / 60) : 0,
    		duration;
    	if (secs < 10) secs = "0" + secs;
    	duration = [mins, secs].join(":");
    	if ($('#playerRightControls .mediaDuration').html() != duration) $('#playerRightControls .mediaDuration').html(duration);
    };
    
    /**
     * Handles media seeking at specific position
     */
    me.seekPosition = function(pos) {
    	if (me.domInstance.seekable.length > 0 && me.domInstance.seekable.start(0) 
    			>= pos <= me.domInstance.seekable.end(0)) me.domInstance.currentTime = pos;
    };
    
    /**
     * Storing currently played segment in a cookie
     * to provide "Continue course" functionality
     */
    me.saveState = function(state) {
        this.parent.helpers.cookie.set('ing_last', JSON.stringify({
            'courseId': app.data.moduleJSON.meta.id,
            'index': state
        }), this.parent.config.cookieTime);
    };

    /**
     * Checks if player is currently in fullscreen mode
     * and turns on/off fullscreen mode.
     */
    me.fullscreenHandle = function(event){
		var player = document.getElementById('video');
		if (me.isFullScreen()) {
    		me.exitFullScreen(); 		
		} else {
			me.enterFullScreen(player); 		
		}
	};
	
    /**
     * Checks if current browser supports fullscreen mode
     */
	me.isFullScreen = function() {
		if (me.playerConfig.html5player.fullscreen_support){
			if (me.playerConfig.html5player.webkit_fullscreen_support){
				return !!document.webkitIsFullScreen;
			} else if (me.playerConfig.html5player.moz_fullscreen_support) {
				return !!document.mozFullScreen;
			} else {
				return !!document.fullscreen;
			}
		} else {
			return $('#video').hasClass('fullscreen');
		}
	};
	
    /**
     * Method responsible for entering to fullscreen mode
     */
	me.enterFullScreen = function(player) {
		if (me.playerConfig.html5player.fullscreen_support){
			if (me.playerConfig.html5player.webkit_fullscreen_support){
				player.webkitRequestFullScreen();
			} else if (me.playerConfig.html5player.moz_fullscreen_support) {
				player.mozRequestFullScreen();
			} else {
				player.requestFullscreen();
			}
		} else {
			if ($('#assignmentPreviewLesson').length){
				$('#assignmentPreviewLesson').appendTo('body');
			}
			$('.mplayerWrapper').toggleClass('fullscreen', true);
			$('body .wrapper').toggleClass('fullscreen', true);
			$(player).toggleClass('fullscreen', true);
			$(window).one('keyup', function(event){
				if (event.keyCode == 27)
					me.exitFullScreen();
			});
			$(document).trigger('fullscreenchange');
		}
	};

    /**
     * Method responsible for exiting from fullscreen mode
     */
	me.exitFullScreen = function() {
		if (me.playerConfig.html5player.fullscreen_support){
			if (me.playerConfig.html5player.webkit_fullscreen_support){
				document.webkitCancelFullScreen();
			} else if (me.playerConfig.html5player.moz_fullscreen_support) {
				document.mozCancelFullScreen();
			} else {
				document.exitFullscreen();
			}
		} else {
			$('#video').toggleClass('fullscreen', false);
			$('.mplayerWrapper').toggleClass('fullscreen', false);
			$('body .wrapper').toggleClass('fullscreen', false);
			$('body').css({'height': 'auto'});
			if ($('#assignmentPreviewLesson').length){
				$('#assignmentPreviewLesson').appendTo('#assignmentPreview .nyroModalWrapper');
			}
			$(document).trigger('fullscreenchange');
		}
	};
    
    /**
     * Visualizes playback state and passes
     * active index to Player API.
     */
    me.play = function(item) {
        var playId = $(item).parent('li').attr('id'),
	    	elements = $("#moduleList").find('li').length;
	    	index = false;
	    	
        $(item).parents('ul').children('li').each( function(i) {
            if(playId == $(this).attr('id')) index = i;
        });
        me.saveState(index);
        $(me.parent.config.module).find('li').each( function(i) {
            if (i == index) {
                $(this).addClass('current');
                Ing.findInDOM().player.api.play(index);                	
            } else {
                $(this).removeClass('current');
            }
        });
    };
    
    /**
     * Recalculates any documents players
     * whem window is resized or rotated
     */
    me.recalculateHtmlPlayer = function() {
        $('.playerHTML5').parent().css({
            'height':  $('#video').height() + 'px',
            'width':  $('#video').width() + 'px'
	    });
	    $('.playerHTML5').css({
	        'height':  ($('#video').height() - 26) + 'px',
	        'width':  $('#video').width() + 'px',
	    });
	    if ($('body .wrapper').hasClass('fullscreen')) {
	    	$('body').css({'height': $('#video').height()});
	    }
	    if ($('.goodbyeMsg').length)
	    	$('.goodbyeMsg').css('top', ($('#video').height() - $('.goodbyeMsg').find('.messageBody').outerHeight())/2);
	    if ($('#mplayer').length) {
	    	var differ = parseInt(($('#mplayer').height() - $('.imagePlayer').height())/2);
			$('.imagePlayer').css('top', (differ < 12)? 0:differ);	
	    }
    };
    
    /**
     * Handles proper video positioning when ipad 
     * rotate event is deteced
     */
    me.handleRotation = function(event) {
	    if (!!me.domInstance && $('video').length) {
	    	$(me.domInstance).height(document.height);
	    }
    };
    
    /**
     * Method responsible for preparing modal window for 
     * HTML5/Flash player. Both players: HTML5 and Flash
     * can be played in modal window and as an embedded players.
     */
    me.playModal = function(obj, playerObj, windowMode){
    	var appConfig = me.parent.config,
        	bg = $('<div class="modalBg"></div>'),
        	parent = me.parent,
        	playerParams;
        bg.css({
            height: $(window).height(),
            width: $(window).width()
        });
        playerObj.css({
            left: $(window).width() / 2 - 350,
            top: 10
        });
        bg.appendTo($('body'));
        playerObj.appendTo($('body'));
        bg.click(function(){
        	playerObj.remove();
            $(me).unbind('click').remove();
        });
		$('.mplayerWrapper .closeFW').click(function(){
			playerObj.remove();
			bg.unbind('click').remove();
		});
	    $('.playerClose').live('click', function() {
	        $('.mplayerWrapper .closeFW').trigger('click');
	    });
	    
	    playerParams = {
				'contentURL': encodeURIComponent(obj.url),
				'cType': parent.data.filetypes[obj.type],
				'duration': encodeURIComponent(obj.duration),
				'pagesNum': encodeURIComponent(obj.pages_num),
				'pages_num': encodeURIComponent(obj.pages_num),
				'allow_downloading': encodeURIComponent(obj.allow_downloading),
				'siteLanguage': siteLanguage
			}
	    
        if (appConfig.player.mode == 'html5') {
        	me.spawnHTML5(appConfig.player.modalSize, playerParams, windowMode);
    	} else {
    		me.domInstance = document.getElementById('video');
    		playerParams.relativeURL = appConfig.mediaURL;
        	me.spawnFlash("mplayer", appConfig.player.modalSize, playerParams, windowMode);
        }  	
    };

    /**
     * Method responsible for preparing embedded version of 
     * HTML5/Flash player. Both players: HTML5 and Flash
     * can be played in modal window and as an embedded players.
     * Additionally this method also handles player resizing when
     * browser window changes its size.
     */
    me.playEmbedded = function(moduleId, type, time, index, duration){
    	var appConfig = me.parent.config,
    		playerHeight = 480,
    		playerWidth = 600,
    		minPlayerHeight = 480,
    		minPlayerWidth = 856,
    		maxPlayerHeight = 600,
    		maxPlayerWidth = 856,
    		ratio = 1.4,
    		playerParams;
    	
        if(!time){
        	time = 10;
        }
        if(!duration){
            duration = 0;
        }

        $(window).resize(function() {
        	calculateNewDimensions();
        });

        function calculateNewDimensions() {
    	    if ( $('#videoWrapper').length ) {
    	      var newPlayerHeight = $(window).height() - 416;
    	      if (newPlayerHeight <= minPlayerHeight) {
    	        playerHeight = minPlayerHeight;
    	      }
    	      else if (newPlayerHeight >= maxPlayerHeight) {
    	        playerHeight = maxPlayerHeight;
    	      }
    	      else {
    	        playerHeight = newPlayerHeight;
    	      }
    	      
    	      var playerWidth = maxPlayerWidth;
    	      $('#videoWrapper').height(playerHeight);
    	      $('#videoWrapper').width(playerWidth);
    	      $('#video').attr('height', playerHeight);
    	      $('#video').attr('width', playerWidth);
    	      if ($('.playerHTML5').length) { me.recalculateHtmlPlayer(); }
    	    };
        }
        
        playerParams = {
    	    'contentURL'      : encodeURIComponent('/content/modules/' + moduleID +
                    						'/?format=json&token='+app.config.ocl_token),
    	    'cType'           : type,
    	    'time'            : time,
    	    'playingIndex'    : playingIndex,
    	    'duration'        : duration,
    	    'siteLanguage'	  : siteLanguage
        }
        
        if (appConfig.player.mode == "html5") {
        	me.spawnHTML5(appConfig.player.embedSize, playerParams, "transparent");
        } else {
        	playerParams.relativeURL = mediaURL;
        	playerParams.contentURL = encodeURIComponent('/content/modules/' + moduleID +
                    							'/?format=xml&token='+app.config.ocl_token);
        	me.spawnFlash("video", appConfig.player.embedSize, playerParams, "transparent");  
        	me.domInstance = document.getElementById('video');
        }
      
        calculateNewDimensions();
        return false;
    };
}
