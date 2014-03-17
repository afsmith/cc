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

    if ($('.registration_form').length && typeof CC_GLOBAL.GETParam.email !== 'undefined') {
        $('.registration_form #id_email').val(qs.email);
    }
});