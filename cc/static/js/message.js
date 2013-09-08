$(document).ready(function(){
    $('#js-addFile').file().choose(function(e, input) {
        input.attr("style", "display: none;");
        input.attr("id", "file");
        input.attr("class", "file");
        input.attr("name", "file");
        $("#file").replaceWith(input);
        $(this).parents('form').submit();
    });
    
    var onSuccessFileImport = function(data) {
        if (data.status == "OK") {
            var file_name_without_ext = data.file_orig_filename.substr(0, data.file_orig_filename.lastIndexOf('.')) || data.file_orig_filename;
            var file_name_full = data.file_orig_filename;

            $('#file_list').append('<li>' + file_name_full + '</li>');

            $('#id_files').val(function() {
                var current_val = $(this).val();
                if (current_val === '') {
                    return data.file_id;
                } else {
                    return current_val + ',' + data.file_id;
                }
            });
            
            /*$("#fileName").text(t.UPLOAD_COMPLETE + ': ' + data.file_orig_filename);
            $('#manageContentForm input[name="title"]').val(
                data.file_orig_filename
                    .substr(0, data.file_orig_filename.lastIndexOf('.')) || data.file_orig_filename
            );
            $("#id_file_id").val(data.file_id);
            $("#mcd").removeClass("button-disabled");
            $('#fileTypeIco').addClass('fileType' + data.file_type);*/

            if (data.is_duration_visible == "True") {
                $("li#duration").show();
            }
            //app.data.changed = true;
        } else {
            $('#js-uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>'+t.ERROR_OCURRED_WITHOUT_DOT + ": " + data["message"]+'</p>')
            console.log(t.SYSTEM_MESSAGE, t.UNSUPPORTED_FILE_TYPE);
        }
    };

    $('#js-uploadFileForm').submit(function() {
        try {
            $("#fileName").text('Uploading: '+$("#file").val());
            $(this).ajaxSubmit({
                success: function(data) {
                    onSuccessFileImport(data);
                    //clearTimeout(app.config.progress.t);
                    $('#progressWrapper').hide();
                    // $('#cancelUpload').hide();
                },
                dataType: 'json'
            });

        } catch(err) {}

        $('#progressWrapper').show();
        $('#cancelUpload').show();
        /*if(typeof app.config.progress != 'object'){
            app.config.progress = {};
        }
        app.config.progress.v = 0;
        app.config.progress.t = false;
        app.config.progress.t = setInterval(function(){
            $('#progress').css({
                'backgroundPosition': (++app.config.progress.v)+'px 0px'
            });
        }, 40);*/
        return false;
    });

    $('#js-submitMessageForm').click(function() {
        $('#js-messageForm').trigger('submit');
        return false;
    });

    $('#id_receivers').tokenfield({
        minLength: 3
    });
});
