/*jslint browser: true, nomen: true, unparam: true*/
/*global $, jQuery, _, CC_GLOBAL, log, escape, unescape*/
'use strict';

var CC_GLOBAL = {};

// ------------------------------- AJAX ------------------------------- //
// get cookie function
CC_GLOBAL.getCookie = function (name) {
    var cookieValue = null,
        cookies,
        cookie,
        i;
    if (document.cookie && document.cookie !== '') {
        cookies = document.cookie.split(';');
        for (i = 0; i < cookies.length; i += 1) {
            cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// CSRF token setup for AJAX
CC_GLOBAL.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function (xhr, settings) {
        if (!CC_GLOBAL.csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", CC_GLOBAL.getCookie('csrftoken'));
        }
    }
});

// handle the spinner
CC_GLOBAL.addSpinner = function () {
    $('body').append('<div class="spinner_overlay"><div class="spinner_center"></div></div>');
};
CC_GLOBAL.removeSpinner = function () {
    $('.spinner_overlay').remove();
};


// ------------------------------- Settings ------------------------------- //
_.templateSettings.variable = 'data';


// --------------------------- Global functions --------------------------- //
// shortcut for console.log()
if (!window.console) {
    window.console = {};
}
if (!window.console.log) {
    window.console.log = function () { return; };
}
var log = (!window.console.log.bind) ? function () { return; } : window.console.log.bind(console);

// global query string function to get query
CC_GLOBAL.GETParam = (function (a) {
    var b = {},
        i,
        p;

    if (a === '') {
        return {};
    }
    for (i = 0; i < a.length; i += 1) {
        p = a[i].split('=');
        if (p.length === 2) {
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, ' '));
        }
    }
    return b;
}(window.location.search.substr(1).split('&')));

// filter table by text
$.expr[':'].Contains = function (a, i, m) {
    return (a.textContent || a.innerText || "").toUpperCase().indexOf(unescape(m[3]).toUpperCase()) >= 0;
};
CC_GLOBAL.filterTable = function (table_body, filter_input) {
    $(filter_input).keyup(function () {
        var filter = $(this).val(),
            table = $(table_body);

        if (filter) {
            filter = escape(filter);
            table.children('tr:not(:Contains(' + filter + '))').hide();
            table.children('tr:Contains(' + filter + ')').show();
        } else {
            table.children('tr').show();
        }

        return false;
    });
};

// show error modal
CC_GLOBAL.showErrorPopup = function (message) {
    $('#js_error_modal .modal-body').text(message);
    $('#js_error_modal').modal();
};

// get browser
CC_GLOBAL.getCurrentBrowser = function () {
    var N = navigator.appName,
        ua = navigator.userAgent,
        tem = ua.match(/version\/([\.\d]+)/i),
        M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\.?\d+(\.\d+)*)/i);
    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+(\.\d+)?)/g.exec(ua) || [];
        return ['IE', (tem[1] || '')];
    }
    if (M && (tem !== null)) {
        M[2] = tem[1];
    }
    M = M ? [M[1], M[2]] : [N, navigator.appVersion];
    return M;  // [browser name, browser version]
};