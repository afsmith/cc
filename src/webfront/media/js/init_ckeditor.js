function initCKEditorHandler() {
    var jq_this = $(this),
        this_name = jq_this.attr('id'),
        basic_editor;

    // destroy instance with the same name
    if (CKEDITOR.instances[this_name])
        CKEDITOR.instances[this_name].destroy();

    // init new instance
    basic_editor = CKEDITOR.replace(this, {
        toolbar: [
            ['Bold', 'Italic'],
            ['NumberedList','BulletedList'],
            ['Format'],
            ['Styles'],
            ['Link','Unlink'],
            ['Undo', 'Redo'],
            ['RemoveFormat'],
            ['Source']
        ],
        height: '150px',
        resize_enabled: false
    });
    jq_this.data('editor', basic_editor);
}