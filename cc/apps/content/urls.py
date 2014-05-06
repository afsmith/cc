from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.content.views',
    url(r'^remove/(?P<file_id>\d+)/$', 'remove_file', name='remove_file'),
    url(r'^upload/$', 'upload_file', name='upload_file'),
    url(r'^upload_image/$', 'upload_image', name='upload_image'),
    url(r'^save_info/$', 'save_file_info', name='save_info'),
)
