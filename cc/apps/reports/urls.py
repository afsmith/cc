from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.reports.views',
    url(r'^(?P<message_id>\d+)/$', 'report_detail', name='report_detail'),
    url(r'^drilldown/$', 'report_drilldown', name='report_drilldown'),
    url(r'^user/$', 'user_log', name='user_log'),
    url(r'^remove_bounce/(?P<bounce_id>\d+)/$',
        'remove_bounce', name='remove_bounce'),
    url(r'^$', 'report_index', name='report_index'),
)
