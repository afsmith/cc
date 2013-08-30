var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();

    var noteChangedMsg = t.NOTE_MODIFIED;
    var saveNoteAction = saveNote;
    app.data.notes = {};

    $('#noteList li').live('click', function(){
        var that = this;
        clearTimeout(app.config.timer);
        app.helpers.checkForm(noteChangedMsg, saveNote, function(){
            $("#noteList .active").removeClass('editing');
            $(that).siblings("li").removeClass("active");
            $(that).addClass("active");
            if($(that).attr("noteid") !== undefined){
                if(!app.data.notes[$(that).attr("noteid")]){
                    $.get("/notepad/notes/" + $(that).attr("noteid") + "/", function(data) {
                       $("#selectedNote").attr("noteid", data.id);
                       $("#noteText").val(data.content);
                       $("#noteTitle").val(data.title);
                       app.data.notes[data.id] = {
                           'title': data.title,
                           'content': data.content
                       }
                    });
                }else{ // saving received note in a local data store
                    $("#selectedNote").attr("noteid", $(that).attr("noteid"));
                    $("#noteText").val(app.data.notes[$(that).attr("noteid")].content);
                    $("#noteTitle").val(app.data.notes[$(that).attr("noteid")].title);
                }
            }else{
                $('#removeNote').hide();
            }
        });
    });

    var saveNote = function() {
        var sendData = {
          "content": $("#noteText").val(),
          "title": $("#noteTitle").val()
        }

        var note_id = $("#selectedNote").attr("noteid");
        if(note_id) {
          sendData["note_id"] = note_id;
        }

        $.post(
            "/notepad/save/",
            JSON.stringify(sendData),
            function(data) {
                if(data.status == "OK") {
                    app.data.dirtyForm = false;
                    $("#selectedNote").attr("noteid", data.note_id);
                    $("#noteList .active").removeClass('editing');
                    var toRemove = $("#note_" + data.note_id);
                    var clone = null;
                    if(toRemove.length > 0) {
                        clone = toRemove.clone();
                        toRemove.remove();
                    } else {
                        clone = $("#noteList li:first").clone();
                        clone.attr("noteid", data.note_id);
                        clone.attr("id", "note_" + data.note_id);
                    }
                    $('#note_dummy').remove();
                    $("#noteList li:first").removeClass("first");
                    clone.find("#title").html(sendData.title);
                    clone.find("#updatedOn").html(app.helpers.timestampToDate(data.updated_on, true));
                    clone.prependTo("#noteList");
                    $("#noteList li:even").removeClass("odd even active").addClass("odd");
                    $("#noteList li:odd").removeClass("odd even active").addClass("even");
                    $("#noteList li:first").addClass("first active");
                    $('#removeNote').show();
                    // -- saving note to local data store
                    if(!app.data.notes[data.note_id]){
                        app.data.notes[data.note_id] = {};
                    }
                    app.data.notes[data.note_id] = sendData;
                }
        });
    };

    var saveNoteWithTimeout = function() {
        clearTimeout(app.config.timer);
        app.config.timer = setTimeout(function(){
            //console.log('saving...');
            saveNote();
        }, 3000);
        //console.log(app.config.timer);
    };

    $('#saveNewNote').live('click', function(){
        saveNote();
        app.helpers.window(
           t.NOTE_SAVED,
           t.NOTE_SAVED
        );
       return false;
    });

    $('#noteText').keyup(function(event){
        app.data.dirtyForm = true;
        $("#noteList .active").addClass('editing');
        saveNoteWithTimeout();
    });

    $('#noteTitle').keyup(function(event){
        app.data.dirtyForm = true;
        if(event.keyCode == 13){
            $('#noteText').focus();
        }
        $("#noteList .active").addClass('editing');
        saveNoteWithTimeout();
    });

    $('#addNewNote').live('click', function() {
        var that = this;
        clearTimeout(app.config.timer);
        app.helpers.checkForm(noteChangedMsg, saveNote, function(){
            $("#selectedNote").removeAttr("noteid");
            $("#noteText").val("");
            $("#noteTitle").val(t.NOTE_DEFAULT_TITLE);
            saveNote();
        });
        toggleDefultValue();
    });

    $('#removeNote').live('click', function(){
        app.helpers.window(
           t.REMOVE_NOTE,
           t.NOTE_REMOVE_CONFIRM + '<br />' + t.CANNOT_BE_UNDONE + '<br/>',
           [{
               'text': t.YES,
               events: [{
                   name: 'click',
                   handler: function(){
                       $.nmTop().close();
                       $.post(
                           "/notepad/notes/" + $("#selectedNote").attr("noteid") + "/delete/",
                           function(data){
                            if(data.status == "OK") {
                                var toRemove = $("#noteList li#note_" + $("#selectedNote").attr("noteid"));

                                // -- removing note from a local data store
                                delete app.data.notes[$("#selectedNote").attr("noteid")];

                                if(toRemove.next().length > 0){
                                    toRemove.next().click();
                                }else if(toRemove.prev().length > 0){
                                    toRemove.prev().click();
                                }else{
                                    $("#selectedNote").removeAttr("noteid");
                                    $("#noteText").val("");
                                    $("#noteTitle").val(t.NOTE_DEFAULT_TITLE);
                                    $("#noteList").append('<li id="note_dummy" class="first"><span id="title">' +
                                        t.NO_NOTES + '</span><br /><span id="updatedOn"></span></li>');
                                    $('#removeNote').hide();
                                }
                                toRemove.remove();
                            }
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

    $("#noteList :first").click();
    if(!$("#selectedNote").attr("noteid")){
        $("#noteTitle").val(t.NOTE_DEFAULT_TITLE);
    }
    $('#userBadge a, #menuWrapper a').click(function(e){
       e.preventDefault();
       var that = this;
       clearTimeout(app.config.timer);
       app.helpers.checkForm(noteChangedMsg, saveNote, function(){
           document.location.href = $(that).attr('href');
       });
    });

    toggleDefultValue();

});

function toggleDefultValue() {
    $('#selectedNote #noteTitle').focus(function() {
    	if(t.NOTE_DEFAULT_TITLE == $('#selectedNote #noteTitle').val()) {
    		$('#selectedNote #noteTitle').val('');
    	}
    });
    $('#selectedNote #noteTitle').blur(function() {
    	if($('#selectedNote #noteTitle').val() == '') {
    		$('#selectedNote #noteTitle').val(t.NOTE_DEFAULT_TITLE);
    	}
    });
}
