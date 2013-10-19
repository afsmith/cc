$(document).ready(function () {
    $('#js_selectMessage').change(function () {
        window.location = '/report/' + $(this).val();
    });
}); // end document ready