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

// shortcut for console.log()
if (!window.console) window.console = {};
if (!window.console.log) window.console.log = function () {};
var log = window.console.log.bind(console);