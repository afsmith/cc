from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.tracking.views',
    url(r'^email/(?P<message_id>\d+)/(?P<user_id>\d+)/$',
        'track_email', name='track_email'),
    url(r'^event/create/$', 'create_event', name='create_event'),
    url(r'^close_deal/$', 'close_deal', name='close_deal'),
    url(r'^link/(?P<message_id>\d+)/(?P<key>[A-Za-z0-9]{1,22})/$',
        'track_link', name='track_link'),
)
