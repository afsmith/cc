$(document).ready(function () {
    var qs = (function(a) {
        if (a === '') return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, ' '));
        }
        return b;
    })(window.location.search.substr(1).split('&'));

    $('#js-loginButton').click(function () {
        $('#loginForm').submit();
        return false;
    });

    // enter to submit
    $('#loginForm input').keyup(function (event) {
        if (event.keyCode === 13) {
           $('#loginForm').submit();
        }
    });

    if ($('.registration_form').length && qs.email !== '') {
        $('.registration_form #id_email').val(qs.email);
    }
});