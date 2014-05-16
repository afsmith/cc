/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log*/
'use strict';

$.validator.addMethod(
    'regex',
    function (value, element, regexp) {
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    'Please include your keyword(s).'
);

$.validator.addMethod(
    'check_token',
    function (value, element) {
        // count the current link
        var count = $('.js_link_text').length,
            content = $('#id_message').code(),
            i,
            current_token;

        for (i = 1; i <= count; i += 1) {
            current_token = '[link' + i + ']';
            if (content.indexOf(current_token) === -1) {
                return false;
            }
        }

        return true;
    },
    'The [link] token should not be removed, it will be replaced with the link your recipient will click. Please add it back.'
);