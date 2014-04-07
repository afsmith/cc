// custom validator
$.validator.addMethod(
    'regex',
    function(value, element, regexp) {
        var check = false;
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    'Please include your keyword(s).'
);

$(document).ready(function () {
    var message_form = $('#js_messageForm'),
        message_submit_btn = $('#js_submitMessageForm'),
        message_field = $('#id_message'),
        to_field = $('#id_to'),
        attachment_field = $('#id_attachment'),
        signature_field = $('#id_signature'),
        upload_form = $('#uploadFileForm'),
        initSignatureField,
        toggleMessageSubmitButton,
        renderUploadError,
        resetUploadForm,
        uploadImage,
        summernote_config_global = {
            toolbar: [
                ['style', ['bold', 'italic', 'underline', 'clear',]],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol']],
                ['insert', [/*'picture',*/ 'link']],
                ['options', ['codeview']],
            ],
            disableDragAndDrop: true,
            onImageUpload: function(files, editor, welEditable) {
                uploadImage(files[0], editor, welEditable);
            },
            keyMap: {
                pc: {
                    'CTRL+Z': 'undo',
                    'CTRL+Y': 'redo',
                    'TAB': 'tab',
                    'SHIFT+TAB': 'untab',
                    'CTRL+B': 'bold',
                    'CTRL+I': 'italic',
                    'CTRL+U': 'underline',
                },
                mac: {
                    'CMD+Z': 'undo',
                    'CMD+SHIFT+Z': 'redo',
                    'TAB': 'tab',
                    'SHIFT+TAB': 'untab',
                    'CMD+B': 'bold',
                    'CMD+I': 'italic',
                    'CMD+U': 'underline',
                }
            }
        }
        summernote_config_message = $.extend({}, summernote_config_global, {
            height: 160,
            onkeyup: function(e) {
                // TODO: improve this later by not copying on every key press
                message_field.val(message_field.code());
                message_field.valid();
            }
        }),
        summernote_config_signature = $.extend({}, summernote_config_global, {
            height: 60,
            focus: true
        }),
        this_device = $('#browser_not_supported span.hidden').text(),
        this_browser = CC_GLOBAL.getCurrentBrowser(),
        this_browser_version_int = parseInt(this_browser[1], 10),
        is_supported_browser = true;

// ------------------------ Browser check ------------------------ //

    if (this_device !== 'Desktop') {
        is_supported_browser = false;
    } else {
        log(this_browser);
        switch (this_browser[0]) {
            case 'Chrome':
                if (this_browser_version_int < 7) {
                    is_supported_browser = false;
                }
                break;
            case 'Firefox':
                if (this_browser_version_int < 4) {
                    is_supported_browser = false;
                }
                break;
            case 'Safari':
                if (this_browser_version_int < 6) {
                    is_supported_browser = false;
                }
                break;
            case 'Opera':
                if (this_browser_version_int < 12) {
                    is_supported_browser = false;
                }
                break;
            case 'IE':
                if (this_browser_version_int < 10) {
                    is_supported_browser = false;
                }
                break;
        }
    }

    if (!is_supported_browser) {
        $('#browser_not_supported').removeClass('hidden');
        if (this_device === 'Desktop') {
            $('#browser_not_supported p:eq(0)').hide();
        } else {
            $('#browser_not_supported p:eq(0) span').text(this_browser.join(' '));    
        }
        $('#send_message_wrapper').remove();
    }



// ------------------------ Form init & validation ------------------------ //

    // validation rules for message form
    message_form.validate({
        ignore: '',
        rules: {
            subject: 'required',
            to: 'required',
            message: {required: true, regex: /\[link\]/},
            attachment: 'required',
            link_text: 'required',
        },
        messages: {
            subject: 'Enter the subject.',
            to: 'Enter at least one email address of the recipient.',
            message: {
                required: 'Enter the message.', 
                regex: 'The [link] token should not be removed, it will be replaced with the link your recipient will click. Please add it back.'
            },
            attachment: 'Upload the attachment.',
            link_text: 'Enter the link text.',
        },
        submitHandler: function(form) {
            form.submit();
        },
        onfocusout: function (element) { // check form valid on blur of each element
            $(element).valid();
        },
        showErrors: function(errorMap, error_list) {
            var remapElementForTooltip = function (element) {
                var _element;
                switch (element.prop('id')) {
                    case 'id_to':
                        _element = $('.tokenfield');
                        break
                    case 'id_message':
                        _element = $('.note-editor').eq(0);
                        break;
                    case 'id_attachment':
                        _element = $('#uploadFileForm');
                        break;
                    default:
                        _element = element;
                        break;
                }
                return _element;
            };

            // clean up any tooltips for valid elements
            $.each(this.validElements(), function (index, element) {
                var _element = remapElementForTooltip($(element));
                _element.data('title', '') .removeClass('error').tooltip('destroy');
            });

            // create new tooltips for invalid elements
            $.each(error_list, function (index, error) {
                var _element = remapElementForTooltip($(error.element));

                _element.tooltip('destroy') // destroy any pre-existing tooltip
                    .data('title', error.message)
                    .addClass('error')
                    .tooltip({ // create new tooltip
                        //placement: 'right',
                    }).tooltip('show');
            });
        }
    });

    // image upload handler
    uploadImage = function (file, editor, welEditable) {
        var ajax_request = new FormData();
        ajax_request.append('file', file);

        $.ajax({
            type: 'POST',
            url: '/file/upload_image/',
            data: ajax_request,
            cache: false,
            contentType: false,
            processData: false,
            success: function(resp) {
                if (resp.status === 'OK') {
                    editor.insertImage(welEditable, resp.url);    
                } else {
                    log('ERROR: ' + resp.message)
                }
            }
        });
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
            //toggleMessageSubmitButton(true);
            to_field.valid();
        }
    }).on('removeToken', function (e) {
        to_field.valid();
    });

    $('.token-input').on('blur', function () {
        to_field.valid();
    });

    // summernote config
    message_field.summernote(summernote_config_message);

    // init the message data
    message_field.code(message_field.val());

    // submit the form when clicking Send button
    message_submit_btn.click(function () {
        // copy data from WYSIWYG editor to textarea before submit
        message_field.val(message_field.code());

        // if there are 2 summernote instance => copy the content of signature summernote to input field
        if ($('.note-editor').length === 2) {
            signature_field.val(signature_field.code());    
        }

        // and trigger submit
        message_form.trigger('submit');
        return false;
    });

    $('#js_resetForm').click(function () {
        location.reload(true);
    });

// ------------------------------- Upload ------------------------------- //

    // handle render the upload error
    renderUploadError = function (error_message) {
        upload_form.prepend('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>' + i18('ERROR_OCURRED') + ': ' + error_message + '</p>');
    };

    // reset everything totally
    resetUploadForm = function () {
        upload_form.removeClass('file_uploaded');
        $('label[for="id_key_page"], #id_key_page').hide();
        $('#id_key_page option[value!=""]').remove();
        $('.dz-file-preview').remove();
    };

    // dropzone config for file upload form
    Dropzone.options.uploadFileForm = {
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 40, // MB
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

                attachment_field.valid();
            } else {
                this.removeFile(file);
                resetUploadForm();
                renderUploadError(response.message);
                log('Conversion error: ' + response.original_error);

                $('.dz-error-mark').css('opacity', 1);
                attachment_field.valid();
            }
        },
        error: function (file, errorMessage) {
            if (errorMessage !== 'You can only upload 1 files.') {
                $('.dz-error-mark').css('opacity', 1);
                this.removeFile(file);
                resetUploadForm();
                renderUploadError(errorMessage);
            }
            attachment_field.valid();
        },
        maxfilesexceeded: function (file) {
            renderUploadError('You can attach only one file at a time');
            $('.dz-file-preview:not(.dz-processing)').remove();
            this.removeFile(file);
            attachment_field.valid();
        },
        removedfile: function (file) {
            // if the file hasn't been uploaded
            if (!file.server_id) { return; }
            // remove the file on server
            $.post('/file/remove/' + file.server_id + '/', function () {
                // remove that file from send message form
                $('#id_attachment').val('');

                resetUploadForm();
            });
        }
    };


// ------------------------------- Signature ------------------------------- //
    initSignatureField = function () {
        $('label[for="id_signature"]').show();
        // add apply button here
        $('label[for="id_signature"]').append('<button id="js_applySignature" class="btn btn-default btn-small" style="margin-left:20px">Apply</button>');

        signature_field.summernote(summernote_config_signature);

        if (signature_field.val() !== '') {
            signature_field.code(signature_field.val());
        }
    };

    // on page init, if there is signature, then show signature box
    if (signature_field.val() !== '') {
        $('#js_editSignature').text('Edit signature');
    }

    // click handler for add / edit signature
    $('#js_editSignature').click(function () {
        $(this).hide(0, function () {
            initSignatureField();
        });
        return false;
    });

    $('.send_message_page').on('click', '#js_applySignature', function () {
        var message_obj = $('<div/>').append($.parseHTML(message_field.code()));
        message_obj.find('#signature').html(signature_field.code());
        message_field.code(message_obj.html());
        return false;
    });
}); // end document ready