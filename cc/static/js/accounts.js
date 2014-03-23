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
        if (typeof CC_GLOBAL.GETParam.email !== 'undefined') {
            $('.registration_form #id_email').val(CC_GLOBAL.GETParam.email);    
        }
        if (typeof CC_GLOBAL.GETParam.invitation_code !== 'undefined') {
            $('.registration_form #id_invitation_code').val(CC_GLOBAL.GETParam.invitation_code);    
        }
    }
});