$(document).ready(function () {
    var this_device = $('#browser_not_supported span.hidden').text(),
        this_browser = CC_GLOBAL.getCurrentBrowser(),
        this_browser_version_int = parseInt(this_browser[1], 10),
        is_supported_browser = true;

    console.log(this_browser);

    if (this_device !== 'Desktop') {
        is_supported_browser = false;
    } else {
        switch (this_browser[0]) {
            case 'Chrome':
                if (this_browser_version_int < 7) {
                    is_supported_browser = false;
                }
                break;
            case 'Firefox':
                if (this_browser_version_int < 4) {
                    is_supported_browser = false;
                }
                break;
            case 'Safari':
                if (this_browser_version_int < 6) {
                    is_supported_browser = false;
                }
                break;
            case 'Opera':
                if (this_browser_version_int < 12) {
                    is_supported_browser = false;
                }
                break;
            case 'IE':
                if (this_browser_version_int < 10) {
                    is_supported_browser = false;
                }
                break;
            case 'MSIE':
                if (this_browser_version_int < 10) {
                    is_supported_browser = false;
                }
                break;
        }
    }

    if (!is_supported_browser) {
        $('#browser_not_supported').removeClass('hidden');
        if (this_device !== 'Desktop') {
            $('#browser_not_supported p:eq(0)').hide();
        } else {
            $('#browser_not_supported p:eq(0) span').text(this_browser.join(' '));    
        }
        $('.send_message_wrapper').remove();
    } 

});