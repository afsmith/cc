// custom validator
$.validator.addMethod(
    "regex",
    function(value, element, regexp) {
        var check = false;
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    "Please include your keyword(s)."
);

$(document).ready(function () {
    var message_form = $('#js_messageForm'),
        message_submit_btn = $('#js_submitMessageForm'),
        message_field = $('#id_message'),
        upload_form = $('#uploadFileForm'),
        _toggleMessageSubmitButton,
        _renderUploadError;

    // validation rules for message form
    message_form.validate({
        ignore: '',
        rules: {
            subject: 'required',
            to: 'required',
            message: {required: true, regex: /\[link\]/},
            attachment: 'required',
        },
        errorPlacement: function(error, element) {
            return true;
        },
        submitHandler: function(form) {
            form.submit();
        }
    });

    // function to enable / disable send button
    _toggleMessageSubmitButton = function (force_disable) {
        if (typeof force_disable !== 'undefined' && force_disable) {
            message_submit_btn.addClass('disabled');
        }

        if (message_form.valid()) {
            message_submit_btn.removeClass('disabled');
        } else {
            message_submit_btn.addClass('disabled');
        }
    };

    // use tokenfield for To field
    $('#id_to').tokenfield({
        minLength: 3,
        createTokensOnBlur: true
    }).on('afterCreateToken', function (e) {
        // validate the email
        var re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        var valid = re.test(e.token.value);
        if (!valid) {
            $(e.relatedTarget).addClass('invalid');
            _toggleMessageSubmitButton(true);
        }
    }).on('removeToken', function (e) {
        _toggleMessageSubmitButton();
    });

    // hide key page
    $('label[for="id_key_page"], #id_key_page').hide();

    // bind validation on input keyup
    message_form.find('input[type="text"], textarea').keyup(function () {
        _toggleMessageSubmitButton();
    });

    // summernote config
    message_field.summernote({
        height: 160,
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['color', ['color']],
            ['para', ['ul', 'ol']],
        ],
        onkeyup: function(e) {
            // TODO: improve this later by not copying on every key press
            message_field.val(message_field.code());
            _toggleMessageSubmitButton();
        }
    });

    _renderUploadError = function (error_message) {
        upload_form.prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + t.ERROR_OCURRED_WITHOUT_DOT + ': ' + error_message + '</p>');
    };

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

                // populate key page selector and show
                for (i=1; i<=page_count; i++) {
                    options += '<option value="'+i+'">'+i+'</option>';
                }
                $('#id_key_page').append(options);
                $('label[for="id_key_page"], #id_key_page').show();
                
                // handle some CSS and template
                upload_form.css({'margin-bottom': '110px'});
                $('.dz-success-mark').css('opacity', 1);
                $('.dz-filename').append(' (<span>' + page_count + ' pages</span>)');

                // remove error message 
                upload_form.find('.alert').remove();

                _toggleMessageSubmitButton();
            } else {
                _renderUploadError(response.message);
                console.log('Conversion error: ' + response.original_error);

                $('.dz-error-mark').css('opacity', 1);
                _toggleMessageSubmitButton();
            }
        },
        error: function (file, errorMessage) {
            if (errorMessage !== 'You can only upload 1 files.') {
                $('.dz-error-mark').css('opacity', 1);
                console.log(errorMessage);
            }
            _toggleMessageSubmitButton();
        },
        maxfilesexceeded: function (file) {
            _renderUploadError('You can attach only one file at a time');
            this.removeFile(file);
            _toggleMessageSubmitButton();
        },
    };

    // submit the form when clicking Send button
    message_submit_btn.click(function() {
        if (!$(this).hasClass('disabled')) {
            // copy data from WYSIWYG editor to textarea before submit
            message_field.val(message_field.code());
            message_form.trigger('submit');
        }
        return false;
    });

}); // end document ready