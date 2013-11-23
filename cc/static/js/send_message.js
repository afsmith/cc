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
        signature_field = $('#id_signature'),
        upload_form = $('#uploadFileForm'),
        initSignatureField,
        toggleMessageSubmitButton,
        renderUploadError;

// ------------------------ Form init & validation ------------------------ //

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
    toggleMessageSubmitButton = function (force_disable) {
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
            toggleMessageSubmitButton(true);
        }
    }).on('removeToken', function (e) {
        toggleMessageSubmitButton();
    });

    // bind validation on input keyup
    message_form.find('input[type="text"], textarea').keyup(function () {
        toggleMessageSubmitButton();
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
            toggleMessageSubmitButton();
        },
    });

    // init the message data
    message_field.code(message_field.val());

    // submit the form when clicking Send button
    message_submit_btn.click(function() {
        if (!$(this).hasClass('disabled')) {
            // copy data from WYSIWYG editor to textarea before submit
            message_field.val(message_field.code());
            signature_field.val(signature_field.code());
            message_form.trigger('submit');
        }
        return false;
    });

// ------------------------------- Upload ------------------------------- //

    // handle render the upload error
    renderUploadError = function (error_message) {
        upload_form.prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + i18('ERROR_OCURRED') + ': ' + error_message + '</p>');
    };

    // dropzone config for file upload form
    Dropzone.options.uploadFileForm = {
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 5, // MB
        maxFiles: 1,
        clickable: true,
        acceptedFiles: 'application/pdf,.pdf,.PDF',
        addRemoveLinks: true,
        success: function (file, response) {
            var page_count = response.page_count,
                i = 1,
                options = '',
                upload_form_bottom;

            if (response.status === 'OK') {
                // assign file_id to file object
                file.server_id = response.file_id;

                // add file ID to hidden input
                $('#id_attachment').val(response.file_id);

                // calculate position for key page select box
                upload_form_bottom = upload_form.offset().top + upload_form.height();
                // populate key page selector and show
                for (i=1; i<=page_count; i+=1) {
                    options += '<option value="'+i+'">'+i+'</option>';
                }
                $('#id_key_page').append(options).css('top', upload_form_bottom + 10).show();
                $('label[for="id_key_page"]').css('top', upload_form_bottom - 20).show();
                
                // handle some CSS and template
                upload_form.addClass('file_uploaded');
                $('.dz-success-mark').css('opacity', 1);
                $('.dz-filename').append(' (<span>' + page_count + ' pages</span>)');

                // remove error message 
                upload_form.find('.alert').remove();

                toggleMessageSubmitButton();
            } else {
                renderUploadError(response.message);
                console.log('Conversion error: ' + response.original_error);

                $('.dz-error-mark').css('opacity', 1);
                toggleMessageSubmitButton();
            }
        },
        error: function (file, errorMessage) {
            if (errorMessage !== 'You can only upload 1 files.') {
                $('.dz-error-mark').css('opacity', 1);
                console.log(errorMessage);
            }
            toggleMessageSubmitButton();
        },
        maxfilesexceeded: function (file) {
            renderUploadError('You can attach only one file at a time');
            this.removeFile(file);
            toggleMessageSubmitButton();
        },
        removedfile: function (file) {
            // if the file hasn't been uploaded
            if (!file.server_id) { return; }
            // remove the file on server
            $.post('/remove_file/' + file.server_id, function () {
                // remove that file from send message form
                $('#id_attachment').val('');

                // reset everything
                upload_form.removeClass('file_uploaded');
                $('label[for="id_key_page"], #id_key_page').hide();
                $('#id_key_page option[value!=""]').remove();
                $('.dz-file-preview').remove();
            });
        }
    };


// ------------------------------- Signature ------------------------------- //
    initSignatureField = function (text) {
        $('label[for="id_signature"]').show();
        $('#add_signature').hide();

        if (typeof text !== 'undefined') {
            $('#signature_box').html(text).show();
            $('label[for="id_signature"]').append('<button id="edit_signature" class="js_addSignature btn btn-small">Edit</button>');
        } else {
            signature_field.summernote({
                height: 60,
                toolbar: [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['color', ['color']],
                ],
                focus: true
            });

            if (signature_field.val() !== '') {
                signature_field.code(signature_field.val());
            }

            $('#signature_box').hide();
        }
    };

    // on page init, if there is signature, then show signature box
    if (signature_field.val() !== '') {
        initSignatureField(signature_field.val());
    }

    // click handler for add / edit signature
    $('.send_message_page').on('click', '.js_addSignature', function () {
        $(this).hide(0, function () {
            initSignatureField();
        });
        return false;
    });

}); // end document ready