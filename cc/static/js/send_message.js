/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log, Dropzone*/
'use strict';

$(document).ready(function () {
    var message_form = $('#js_messageForm'),
        message_submit_btn = $('#js_submitMessageForm'),
        message_field = $('#id_message'),
        to_field = $('#id_to'),
        signature_field = $('#id_signature'),
        upload_form = $('#uploadFileForm'),
        file_form = $('.js_file_form'),

        // function
        initSignatureField,
        validateErrorHandler,
        renderUploadError,
        linkTokenHanlder,
        addFileHandler,
        removeFileHandler,
        uploadImage,
        downloadCheckboxHandler,

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
                _element = $('.select2-container');
                break;
            case 'id_message':
                _element = $('.note-editor').eq(0);
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
        },
        messages: {
            subject: 'Enter the subject.',
            to: 'Enter at least one email address of the recipient.',
            message: {
                required: 'Enter the message.',
            },
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

    // use select2 for To field
    to_field.select2({
        width: '100%',
        minimumInputLength: 3,
        multiple: true,
        ajax: {
            url: '/addressbook/search/',
            dataType: 'json',
            quietMillis: 100,
            data: function (input, page) {
                return {
                    q: input,
                };
            },
            results: function (data, page) {
                return {
                    results: $.map(data.contacts, function (item) {
                        return {
                            text: item.work_email,
                            id: item.work_email,
                            first_name: item.first_name,
                            last_name: item.last_name,
                            company: item.company,
                        };
                    })
                };
            },
            cache: true
        },
        formatSelection: function (item) {
            return item.text;
        },
        formatResult: function (item) {
            var text = item.text;

            if (item.first_name || item.last_name) {
                text += ' (' + $.trim(item.first_name + ' ' + item.last_name) + ')';

            }

            if (item.company) {
                text += ' - ' + item.company;
            }

            return text;
        },
        tags: true,
        createSearchChoice: function (term, data) {
            var re = /^[a-zA-Z0-9._\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,4}$/;

            if ($(data).filter(function () {
                    return this.text.localeCompare(term) === 0;
                }).length === 0 && re.test(term)) {
                return {
                    id: term,
                    text: term
                };
            }
        },
        formatNoMatches: function (term) {
            return term + ' is not a valid email address';
        },
        tokenizer: function (input, selection, callback) {
            var parts,
                part,
                i;
            if (input.indexOf(',') < 0) {
                return;
            }

            parts = input.split(/,| /);
            for (i = 0; i < parts.length; i += 1) {
                part = parts[i];
                part = part.trim();

                callback({id: part, text: part});
            }
        }
    }).on('change', function (e) {
        to_field.valid();
    }).on('select2-blur', function () {
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

        if (file_form.valid()) {
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
    file_form.validate({
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
            _.template('<p class="alert"><button type="button" class="close" data-dismiss="alert">&times;</button>An error occurred: <%= data.error %></p>', {
                error: error_message
            })
        );
    };

    // handle show and hide download checkbox
    downloadCheckboxHandler = function () {
        if ($('.js_link_text').length > 0) {
            $('.js_download_clone').removeClass('hidden');
        } else {
            $('.js_download_clone').addClass('hidden');
            $('#id_allow_download').val('False');
        }
    };
    $('#id_download_clone').change(function () {
        if ($(this).is(':checked')) {
            $('#id_allow_download').val('True');
        } else {
            $('#id_allow_download').val('False');
        }
    });


    // handle add and remove link token
    linkTokenHanlder = function (add) {
        var content = message_field.code(),
            previous_token,
            current_token,
            i;

        if (add === true) {
            // add token 1
            if (content.indexOf('[link1]') === -1) {
                if (content.indexOf('<div id="link_token">') > -1) {
                    // if there is link_token div then add inside it
                    content = content.replace('<div id="link_token">', '<div id="link_token">[link1]');
                } else if (content.indexOf('<div id="signature">') > -1) {
                    // if there is signature div then add before it
                    content = content.replace('<div id="signature">', '[link1]<br /><br /><div id="signature">');
                } else {
                    // else, add in the end of message
                    content += '[link1]';
                }
            } else {
                // and other token from lowest first
                for (i = 2; i < 6; i += 1) {
                    previous_token = '[link' + (i - 1) + ']';
                    current_token = '[link' + i + ']';

                    if (content.indexOf(current_token) === -1 && content.indexOf(previous_token) > -1) {
                        content = content.replace(previous_token, previous_token + '<br />' + current_token);
                        break;
                    }
                }
            }
        } else {
            // remove the token from highest first
            for (i = 5; i >= 1; i -= 1) {
                current_token = '[link' + i + ']';
                if (content.indexOf(current_token) > -1) {
                    content = content.replace(current_token, '');
                    break;
                }
            }
        }

        message_field.code(content);
    };

    // handle add file action
    addFileHandler = function (file, resp) {
        var file_id = file.server_id,
            file_preview,
            file_index;

        // add file ID to hidden input
        $('#id_attachment').val(function (index, value) {
            return value + file.server_id + ','; // example: 1,2,3,
        });

        // add file preview ID
        file.previewElement.id = 'js_file_preview_' + file_id;
        file_preview = $('#js_file_preview_' + file_id);

        upload_form.addClass('file_uploaded');
        file_preview.find('.dz-success-mark').css('opacity', 1);
        file_preview.find('.dz-filename').append(' (<span>' + resp.page_count + ' pages</span>)');

        // find the correct file index
        file_index = upload_form.find('.dz-file-preview').index(file_preview) + 1;

        // add link text input + label
        file_form.append(
            _.template('<label for="js_link_text_<%= data.file_id %>" class="js_link_label">Link text <%= data.file_index %></label><input id="js_link_text_<%= data.file_id %>" name="link_text_<%= data.file_index %>" type="text" class="form-control js_link_text" />', {
                file_id: file_id,
                file_index: file_index
            })
        );

        // add link token to message textarea
        linkTokenHanlder(true);

        // handle download checkbox
        downloadCheckboxHandler();

        // remove error message
        upload_form.find('.alert').remove();
    };

    // handle remove file action
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
        if ($('#js_link_text_' + file.server_id).length) {
            $('#js_link_text_' + file.server_id).remove();
            $('label[for="js_link_text_' + file.server_id + '"]').remove();
            $('#js_file_preview_' + file.server_id).remove();
            // remove link token
            linkTokenHanlder();
        } else {
            // in case there is error and the file is removed rightaway
            file.previewElement.parentNode.removeChild(file.previewElement);
        }

        // rename the label on text input
        $('.js_link_label').each(function (index) {
            $(this).text('Link text ' + (index + 1));
        });
        $('.js_link_text').each(function (index) {
            $(this).prop('name', 'link_text_' + (index + 1));
        });

        // download checkbox
        downloadCheckboxHandler();
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
            }
        },
        error: function (file, errorMessage) {
            if (errorMessage !== 'You can only upload 5 files.') {
                renderUploadError(errorMessage);
                this.removeFile(file);
            }
        },
        maxfilesexceeded: function (file) {
            renderUploadError('You can attach maximum 5 files at a time');
            $('.dz-file-preview:not(.dz-processing)').remove();
            this.removeFile(file);
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
