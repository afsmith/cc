$(document).ready(function(){

    $('#js-uploadFileForm').dropzone({
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 5, // MB
        maxFiles: 1,
        clickable: true,
        acceptedFiles: 'application/pdf',
        uploadprogress: function (a, progress) {
            console.log(progress);
        },
        success: function (file, resp) {
            console.log(file);
            console.log(resp);
            if (resp.status === 'OK') {
                //var file_name_without_ext = resp.file_orig_filename.substr(0, resp.file_orig_filename.lastIndexOf('.')) || resp.file_orig_filename;
                //var file_name_full = resp.file_orig_filename;

                //$('#file_list').append('<li>' + file_name_full + '</li>');
                $('#id_attachment').val(resp.file_id);

                // remove error message 
                $('#js-uploadFileForm .alert').remove();
            } else {
                $('#js-uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ": " + resp.message + '</p>');
                console.log(t.SYSTEM_MESSAGE, t.UNSUPPORTED_FILE_TYPE);
            }
        },
        maxfilesexceeded: function () {
            console.log('Max file exceed');
        },
    });

    $('#js-submitMessageForm').click(function() {
        if (!$(this).hasClass('disabled')) {
            console.log('jaj');
            $('#js-messageForm').trigger('submit');
        }
        return false;
    });

    $('#id_to').tokenfield({
        minLength: 3
    });
});
