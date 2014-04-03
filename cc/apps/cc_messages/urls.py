from django.conf.urls import patterns, url

urlpatterns = patterns(
    'cc.apps.cc_messages.views',
    url(r'^send/$', 'send_message', name='send_message'),
    url(r'^resend/$', 'resend_message', name='resend_message'),
)
