from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^accounts/login/$', 'management.views.login_screen', name="auth_login"),
    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'}),

#    url(r'^accounts/', include('self_register.urls')),
    url(r'^accounts/ocl/$', 'management.views.one_click_link'),

    # home
    url(r'^$', 'webfront.views.home', name='home'),
    url(r'^upload/$', 'webfront.views.upload_file', name='upload_file'),


    # old URLs
#    url(r'^administration/', include('administration.urls')),
    url(r'^content/', include('content.urls')),
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^management/', include('management.urls')),
    url(r'^assignments/', include('assignments.urls')),
    url(r'^tracking/', include('tracking.urls')),
#    url(r'^tagging/', include('tagging.urls')),
#    url(r'^messages/', include('messages_custom.urls')),
#    url(r'^notepad/', include('notepad.urls')),
#    url(r'^reports/', include('reports.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]

    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % media_url,
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
