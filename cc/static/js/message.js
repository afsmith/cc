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
        success: function (file, response) {
            if (response.status === 'OK') {
                $('#id_attachment').val(response.file_id);

                // remove error message 
                $('#js-uploadFileForm .alert').remove();
            } else {
                $('#js-uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ": " + response.message + '</p>');
                console.log('Conversion error: ' + response.original_error);
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