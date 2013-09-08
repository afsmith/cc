$(document).ready(function () {

    $('#js-loginButton').click(function () {
        $('#loginForm').submit();
        return false;
    });

    $('#loginForm input').keyup(function (event) {
        if (event.keyCode === 13) {
           $('#loginForm').submit();
        }
    });
});