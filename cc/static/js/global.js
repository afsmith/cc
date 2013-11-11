var CC_GLOBAL = CC_GLOBAL || {};

CC_GLOBAL.csrftoken = $.cookie('csrftoken');

CC_GLOBAL.csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};
CC_GLOBAL.sameOrigin = function (url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
};

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!CC_GLOBAL.csrfSafeMethod(settings.type) && CC_GLOBAL.sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", CC_GLOBAL.csrftoken);
        }
    }
});

// global function to get translated text
var i18 = function (key) {
    if (key in CC_GLOBAL.i18n) {
        return CC_GLOBAL.i18n[key];
    } else {
        console.log('No translation is available for: ' + key);
        return key;
    }
};