from django.conf.urls import patterns, url

urlpatterns = patterns('',
    #url(r'^view_smm/(?P<id>\d+)/$', views.view_module_smm, name='content-view_module_smm'),
    url(r'^view/(?P<id>\d+)/$', 
        'cc.apps.content.views.view_course', name='content-view_course'),
)
