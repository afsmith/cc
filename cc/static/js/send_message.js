/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log, Dropzone, i18*/
'use strict';

$(document).ready(function () {
    var message_form = $('#js_messageForm'),
        message_submit_btn = $('#js_submitMessageForm'),
        message_field = $('#id_message'),
        to_field = $('#id_to'),
        attachment_field = $('#id_attachment'),
        signature_field = $('#id_signature'),
        upload_form = $('#uploadFileForm'),
        link_text_form = $('.js_link_texts'),

        // function
        initSignatureField,
        validateErrorHandler,
        renderUploadError,
        linkTokenHanlder,
        addFileHandler,
        removeFileHandler,
        uploadImage,

        // config
        summernote_config_global = {
            toolbar: [
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol']],
                ['insert', ['link', 'picture'/*, 'video'*/]],
                ['options', ['codeview']],
            ],
            disableDragAndDrop: true,
            onImageUpload: function (files, editor, welEditable) {
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
        },
        summernote_config_message = $.extend({}, summernote_config_global, {
            height: 250,
            onkeyup: function () {
                // TODO: improve this later by not copying on every key press
                message_field.val(message_field.code());
                message_field.valid();
            }
        }),
        summernote_config_signature = $.extend({}, summernote_config_global, {
            height: 60,
            focus: true
        });


// ------------------------ Form init & validation ------------------------ //
    validateErrorHandler = function (errorMap, error_list) {
        var remapElementForTooltip = function (element) {
            var _element;
            switch (element.prop('id')) {
            case 'id_to':
                _element = $('.tokenfield');
                break;
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
            _element.data('title', '').removeClass('error').tooltip('destroy');
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
    };

    // validation rules for message form
    message_form.validate({
        ignore: '',
        rules: {
            subject: 'required',
            to: 'required',
            message: {required: true, check_token: true},
            attachment: 'required',
        },
        messages: {
            subject: 'Enter the subject.',
            to: 'Enter at least one email address of the recipient.',
            message: {
                required: 'Enter the message.',
            },
            attachment: 'Upload the attachments.',
        },
        submitHandler: function (form) {
            form.submit();
        },
        onfocusout: function (element) { // check form valid on blur of each element
            $(element).valid();
        },
        showErrors: validateErrorHandler
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
            success: function (resp) {
                if (resp.status === 'OK') {
                    editor.insertImage(welEditable, resp.url);
                } else {
                    log('ERROR: ' + resp.message);
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
        var re = /^[a-zA-Z0-9._\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,4}$/,
            valid = re.test(e.token.value);
        if (!valid) {
            $(e.relatedTarget).addClass('invalid');
            //toggleMessageSubmitButton(true);
            to_field.valid();
        }
    }).on('removeToken', function () {
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

        if (link_text_form.valid()) {
            // get the request data here
            var request_data = {};
            $('.js_link_text').each(function () {
                var _this = $(this),
                    file_id = parseInt(_this.prop('id').replace('js_link_text_', ''), 0),
                    file_index = parseInt(_this.prop('name').replace('link_text_', ''), 0);
                request_data[file_id + '.index'] = file_index;
                request_data[file_id + '.value'] = _this.val();
            });

            $.ajax({
                type: 'POST',
                url: '/file/save_info/',
                cache: false,
                data: request_data
            }).done(function () {
                // and trigger submit
                message_form.trigger('submit');
            });
        }

        return false;
    });

    $('#js_resetForm').click(function () {
        location.reload(true);
        return false;
    });

// ------------------------------- Upload ------------------------------- //
    link_text_form.validate({
        ignore: '',
        rules: {
            link_text_1: 'required',
            link_text_2: 'required',
            link_text_3: 'required',
            link_text_4: 'required',
            link_text_5: 'required',
        },
        messages: {
            link_text_1: 'Enter the link text',
            link_text_2: 'Enter the link text',
            link_text_3: 'Enter the link text',
            link_text_4: 'Enter the link text',
            link_text_5: 'Enter the link text',
        },
        onfocusout: function (element) { // check form valid on blur of each element
            $(element).valid();
        },
        showErrors: validateErrorHandler
    });

    // handle render the upload error
    renderUploadError = function (error_message) {
        upload_form.addClass('error');
        upload_form.prepend(
            _.template('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button><%= data.error %>: <%= data.message %></p>', {
                error: i18('ERROR_OCURRED'),
                message: error_message
            })
        );
    };

    linkTokenHanlder = function (add) {
        var content = message_field.code(),
            current_token,
            i;

        if (add === true) {
            for (i = 2; i < 6; i += 1) {
                current_token = '[link' + i + ']';
                if (content.indexOf(current_token) === -1) {
                    content += current_token;
                    break;
                }
            }
        } else {
            for (i = 5; i > 1; i -= 1) {
                current_token = '[link' + i + ']';
                if (content.indexOf(current_token) > -1) {
                    content = content.replace(current_token, '');
                    break;
                }
            }
        }

        message_field.code(content);
    };

    addFileHandler = function (file, resp) {
        var file_id = file.server_id,
            file_index = upload_form.find('.dz-filename').length,
            file_preview;

        // add file ID to hidden input
        $('#id_attachment').val(function (index, value) {
            return value + file.server_id + ','; // example: 1,2,3,
        });

        // add link text input + label
        $('.js_link_texts').append('<label for="js_link_text_' + file_id + '" class="js_link_label">Link text ' + file_index + '</label><input id="js_link_text_' + file_id + '" name="link_text_' + file_index + '" type="text" class="form-control js_link_text" />');

        // add id to preview
        file.previewElement.id = 'js_file_preview_' + file_id;
        file_preview = $('#js_file_preview_' + file_id);

        // add link token to message textarea
        if (file_index > 1) {
            linkTokenHanlder(true);
        }

        // handle some CSS and template
        upload_form.addClass('file_uploaded');
        file_preview.find('.dz-success-mark').css('opacity', 1);
        file_preview.find('.dz-filename').append(' (<span>' + resp.page_count + ' pages</span>)');

        // remove error message 
        upload_form.find('.alert').remove();

        attachment_field.valid();
    };

    removeFileHandler = function (file) {
        // if the file hasn't been uploaded
        if (!file.server_id) { return; }

        // remove the file on server
        $.post('/file/remove/' + file.server_id + '/', function () {
            // remove that file from attachment field
            $('#id_attachment').val(function (index, value) {
                return value.replace(file.server_id + ',', '');
            });
        });

        // remove the preview, link text input + label
        file.previewElement.parentNode.removeChild(file.previewElement);
        $('#js_link_text_' + file.server_id).remove();
        $('label[for="js_link_text_' + file.server_id + '"]').remove();
        $('#js_file_preview_' + file.server_id).remove();

        // remove link token
        linkTokenHanlder();

        // rename the label on text input
        $('.js_link_label').each(function (index) {
            $(this).text('Link text ' + (index + 1));
        });
        $('.js_link_text').each(function (index) {
            $(this).prop('name', 'link_text_' + (index + 1));
        });
    };

    // dropzone config for file upload form
    Dropzone.options.uploadFileForm = {
        url: $(this).attr('action'),
        paramName: 'file',
        maxFilesize: 40, // MB
        maxFiles: 5,
        clickable: true,
        acceptedFiles: 'application/pdf,.pdf,.PDF',
        addRemoveLinks: true,
        success: function (file, response) {
            // assign file_id to file object
            file.server_id = response.file_id;

            if (response.status === 'OK') {
                addFileHandler(file, response);
            } else {
                this.removeFile(file);
                renderUploadError(response.message);
                log('Conversion error: ' + response.message);

                attachment_field.valid();
            }
        },
        error: function (file, errorMessage) {
            if (errorMessage !== 'You can only upload 5 files.') {
                renderUploadError(errorMessage);
                this.removeFile(file);
            }
            attachment_field.valid();
        },
        maxfilesexceeded: function (file) {
            renderUploadError('You can attach maximum 5 files at a time');
            $('.dz-file-preview:not(.dz-processing)').remove();
            this.removeFile(file);
            attachment_field.valid();
        },
        removedfile: removeFileHandler
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

    $('.send_message_wrapper').on('click', '#js_applySignature', function () {
        var message_obj = $('<div/>').append($.parseHTML(message_field.code()));
        message_obj.find('#signature').html(signature_field.code());
        message_field.code(message_obj.html());
        return false;
    });
}); // end document ready