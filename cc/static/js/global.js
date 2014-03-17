var CC_GLOBAL = CC_GLOBAL || {};

// CSRF token setup for AJAX
CC_GLOBAL.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!CC_GLOBAL.csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});

// global function to get translated text
var i18 = function (key) {
    if (key in CC_GLOBAL.i18n) {
        return CC_GLOBAL.i18n[key];
    } else {
        console.log('[NOTICE] No translation is available for: ' + key);
        return key;
    }
};

// global query string function to get query
CC_GLOBAL.GETParam = (function(a) {
    if (a === '') return {};
    var b = {};
    for (var i = 0; i < a.length; i+=1) {
        var p = a[i].split('=');
        if (p.length != 2) continue;
        b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, ' '));
    }
    return b;
})(window.location.search.substr(1).split('&'));

// shortcut for console.log()
if (!window.console) window.console = {};
if (!window.console.log) window.console.log = function () {};
var log = (!window.console.log.bind) ? function () {} : window.console.log.bind(console);