/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL*/
'use strict';

$(document).ready(function () {
    $('#js_loginButton').click(function () {
        $('#loginForm').submit();
        return false;
    });

    // enter to submit
    $('#loginForm input').keyup(function (event) {
        if (event.keyCode === 13) {
            $('#loginForm').submit();
        }
    });

    if ($('.registration_form').length) {
        if (!_.isUndefined(CC_GLOBAL.GETParam.email)) {
            $('.registration_form #id_email').val(CC_GLOBAL.GETParam.email);
        }
        if (!_.isUndefined(CC_GLOBAL.GETParam.invitation_code)) {
            $('.registration_form #id_invitation_code').val(CC_GLOBAL.GETParam.invitation_code);
        }

        // for zappier
        if (!_.isUndefined(CC_GLOBAL.GETParam.id_first_name)) {
            $('.registration_form #id_first_name').val(CC_GLOBAL.GETParam.id_first_name);
        }
        if (!_.isUndefined(CC_GLOBAL.GETParam.id_last_name)) {
            $('.registration_form #id_last_name').val(CC_GLOBAL.GETParam.id_last_name);
        }
        if (!_.isUndefined(CC_GLOBAL.GETParam.id_email1)) {
            $('.registration_form #id_email1').val(CC_GLOBAL.GETParam.id_email1);
        }
        if (!_.isUndefined(CC_GLOBAL.GETParam.id_f_key)) {
            $('.registration_form #id_f_key').val(CC_GLOBAL.GETParam.id_f_key);
        }

    }
});