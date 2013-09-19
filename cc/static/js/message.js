$(document).ready(function () {

    $('#js-uploadFileForm').dropzone({
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 5, // MB
        maxFiles: 1,
        clickable: true,
        acceptedFiles: 'application/pdf',
        uploadprogress: function (foo, progress) {
            console.log(progress);
        },
        success: function (file, resp) {
            if (resp.status === 'OK') {
                $('#id_attachment').val(resp.file_id);

                // remove error message 
                $('#js-uploadFileForm .alert').remove();
            } else {
                $('#js-uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ": " + resp.message + '</p>');
                console.log(t.SYSTEM_MESSAGE, t.UNSUPPORTED_FILE_TYPE);
            }
        },
        error: function (file, errorMessage) {
            console.log(errorMessage);
        },
        maxfilesexceeded: function () {
            console.log('Max file exceed');
        },
    });

    $('#js-submitMessageForm').click(function() {
        if (!$(this).hasClass('disabled')) {
            $('#js-messageForm').trigger('submit');
        }
        return false;
    });

    $('#id_to').tokenfield({
        minLength: 3
    });

}); // end document ready