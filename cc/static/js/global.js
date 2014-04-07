var CC_GLOBAL = CC_GLOBAL || {};

// ------------------------------- AJAX ------------------------------- //
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

// handle the spinner
CC_GLOBAL.addSpinner = function () {
    $('body').append('<div class="spinner_overlay"><div class="spinner_center"></div></div>');
};
CC_GLOBAL.removeSpinner = function () {
    $('.spinner_overlay').remove();
};


// --------------------------- Global functions --------------------------- //
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
var log = (!window.console.log.bind) ? function () {} : window.console.log.bind(console);

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


// filter table by text
$.expr[':'].Contains = function(a,i,m){
    return (a.textContent || a.innerText || "").toUpperCase().indexOf(unescape(m[3]).toUpperCase())>=0;
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
CC_GLOBAL.showErrorPopup = function(message) {
    $('#js_error_modal .modal-body').text(message);
    $('#js_error_modal').modal();
}
