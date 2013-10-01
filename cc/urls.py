from django.conf.urls import patterns, include, url
from django.conf import settings

from cc.apps.accounts.forms import UserCreationForm, UserPasswordResetForm
from registration.backends.default.views import RegistrationView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    # ----- CC APP  ----- #
    url(r'^$', 'cc.apps.cc_messages.views.send_message', name='home'),
    url(r'^report/$', 'cc.apps.cc.views.report', name='report'),
    url(r'^upload/$', 'cc.apps.content.views.upload_file', name='upload_file'),
    url(r'^view/(?P<id>\d+)/$',
        'cc.apps.cc_messages.views.view_message', name='view_message'),
    # tracking email opened
    url(r'^track/(?P<message_id>\d+)/(?P<user_id>\d+)$',
        'cc.apps.cc_messages.views.track_email', name='track_email'),


    # registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=UserCreationForm)),
    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'),
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset', 
        {'password_reset_form': UserPasswordResetForm},
        name='auth_password_reset'),
    url(r'^accounts/', include('registration.backends.default.urls')),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]

    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % media_url,
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )
