$(document).ready(function () {

    Dropzone.options.uploadFileForm = {
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 5, // MB
        maxFiles: 1,
        clickable: true,
        acceptedFiles: 'application/pdf',
        success: function (file, response) {
            if (response.status === 'OK') {
                // add file ID to hidden input
                $('#id_attachment').val(response.file_id);

                // handle some CSS and template
                $('.dz-success-mark').css('opacity', 1);
                $('.dz-filename').append(' (<span>' + response.page_count + ' pages</span>)');

                // remove error message 
                $('#uploadFileForm .alert').remove();

                // enable button
                $('#js-submitMessageForm').removeClass('disabled');
            } else {
                $('#uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ": " + response.message + '</p>');

                $('.dz-error-mark').css('opacity', 1);
                console.log('Conversion error: ' + response.original_error);
            }
        },
        error: function (file, errorMessage) {
            $('.dz-error-mark').css('opacity', 1);
            console.log(errorMessage);
        },
        maxfilesexceeded: function () {
            console.log('Max file exceed');
        },
    };

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