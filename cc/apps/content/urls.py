from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^view/(?P<id>\d+)/$',
        'cc.apps.content.views.view_course', name='content-view_course'),
)
