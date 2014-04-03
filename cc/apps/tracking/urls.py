from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.tracking.views',
    url(r'^email/(?P<message_id>\d+)/(?P<user_id>\d+)/$',
        'track_email', name='track_email'),
    url(r'^event/create/$', 'create_event', name='create_event'),
    url(r'^close_deal/$', 'close_deal', name='close_deal'),
)
