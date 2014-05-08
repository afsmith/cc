from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    # ----- CC Apps  ----- #
    url(r'^accounts/',  include('cc.apps.accounts.urls')),
    url(r'^message/',  include('cc.apps.cc_messages.urls')),
    url(r'^track/',  include('cc.apps.tracking.urls')),
    url(r'^report/',  include('cc.apps.reports.urls')),
    url(r'^file/',  include('cc.apps.content.urls')),
    url(r'^payments/',  include('cc.apps.cc_stripe.urls')),

    # ----- Individual patterns  ----- #
    url(r'^$', 'cc.apps.main.views.dashboard', name='home'),
    url(r'^view/(?P<message_id>\d+)/(?P<file_index>\d+)/$',
        'cc.apps.cc_messages.views.view_message', name='view_message'),
    url(r'^sendgrid_parse/$',
        'cc.apps.main.views.sendgrid_parse', name='sendgrid_parse'),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]

    urlpatterns += patterns(
        '',
        url(r'^%s(?P<path>.*)$' % media_url,
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT})
    )
