$(document).ready(function () {
    var message_form = $('#js-messageForm'),
        message_submit_btn = $('#js-submitMessageForm');

    // validation rules for message form
    message_form.validate({
        ignore: '',
        rules: {
            subject: 'required',
            to: 'required',
            message: 'required',
            attachment: 'required',
        },
        errorPlacement: function(error,element) {
            return true;
        },
        submitHandler: function(form) {
            form.submit();
        }
    });

    // function to enable / disable send button
    function toggleMessageSubmitButton(force_disable) {
        if (typeof force_disable !== 'undefined' && force_disable) {
            message_submit_btn.addClass('disabled');
        }

        if (message_form.valid()) {
            message_submit_btn.removeClass('disabled');
        } else {
            message_submit_btn.addClass('disabled');
        }
    }

    // bind validation on input keyup
    message_form.find('input[type="text"], textarea').keyup(function () {
        toggleMessageSubmitButton();
    });

    // submit the form when clicking Send button
    message_submit_btn.click(function() {
        if (!$(this).hasClass('disabled')) {
            message_form.trigger('submit');
        }
        return false;
    });

    // use tokenfield for To field
    $('#id_to').tokenfield({
        minLength: 3
    }).on('afterCreateToken', function (e) {
        // validate the email
        var re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        var valid = re.test(e.token.value);
        if (!valid) {
            $(e.relatedTarget).addClass('invalid');
            toggleMessageSubmitButton(true);
        }
    }).on('removeToken', function (e) {
        toggleMessageSubmitButton();
    });

    // hide pricing page
    $('label[for="id_pricing_page"], #id_pricing_page').hide();

    // dropzone config for file upload form
    Dropzone.options.uploadFileForm = {
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 5, // MB
        maxFiles: 1,
        clickable: true,
        acceptedFiles: 'application/pdf,.pdf,.PDF',
        success: function (file, response) {
            var page_count = response.page_count,
                i = 1,
                options = '';

            if (response.status === 'OK') {
                // add file ID to hidden input
                $('#id_attachment').val(response.file_id);

                // populate pricing page selector and show
                for (i=1; i<=page_count; i++) {
                    options += '<option value="'+i+'">'+i+'</option>';
                }
                $('#id_pricing_page').append(options);
                $('label[for="id_pricing_page"], #id_pricing_page').show();
                

                // handle some CSS and template
                $('.dz-success-mark').css('opacity', 1);
                $('.dz-filename').append(' (<span>' + page_count + ' pages</span>)');

                // remove error message 
                $('#uploadFileForm .alert').remove();

                toggleMessageSubmitButton();
            } else {
                $('#uploadFileForm').prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ": " + response.message + '</p>');
                console.log('Conversion error: ' + response.original_error);

                $('.dz-error-mark').css('opacity', 1);
                toggleMessageSubmitButton();
            }
        },
        error: function (file, errorMessage) {
            $('.dz-error-mark').css('opacity', 1);
            console.log(errorMessage);
            toggleMessageSubmitButton();
        },
        maxfilesexceeded: function () {
            console.log('Max file exceed');
            toggleMessageSubmitButton();
        },
    };

}); // end document ready