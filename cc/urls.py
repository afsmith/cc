from django.conf.urls import patterns, include, url
from django.conf import settings

from cc.apps.accounts.forms import UserCreationForm, UserPasswordResetForm
from registration.backends.default.views import RegistrationView
from django.contrib.auth.decorators import login_required

from django.contrib import admin
admin.autodiscover()

from cc.apps.cc_stripe.views import (
    CancelView,
    SubscribeView,
    NewSubscriberView,
)


urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

    # ----- CC APP  ----- #
    url(r'^$', 'cc.apps.main.views.dashboard', name='home'),
    url(r'^send/$', 'cc.apps.cc_messages.views.send_message', name='send'),
    url(r'^upload/$', 'cc.apps.content.views.upload_file', name='upload_file'),
    url(r'^upload_image/$',
        'cc.apps.content.views.upload_image', name='upload_image'),
    #url(r'^view/(?P<message_id>\d+)/$',
    #    'cc.apps.cc_messages.views.view_message', name='view_message'),
    url(r'^view/(?P<message_id>\d+)/$',
        'cc.apps.cc_messages.views.view_message', name='view_message'),

    url(r'^resend/$',
        'cc.apps.cc_messages.views.resend_message', name='resend'),

    url(r'^remove_file/(?P<file_id>\d+)/$',
        'cc.apps.content.views.remove_file', name='remove_file'),

    # tracking
    url(r'^track/email/(?P<message_id>\d+)/(?P<user_id>\d+)/$',
        'cc.apps.tracking.views.track_email', name='track_email'),
    url(r'^track/event/create/$',
        'cc.apps.tracking.views.create_event', name='create_event'),
    url(r'^track/close_deal/$',
        'cc.apps.tracking.views.close_deal', name='close_deal'),

    # report
    url(r'^report/(?P<message_id>\d+)/$',
        'cc.apps.reports.views.report_detail', name='report_detail'),
    url(r'^report/drilldown/$',
        'cc.apps.reports.views.report_drilldown', name='report_drilldown'),
    url(r'^report/user/$',
        'cc.apps.reports.views.user_log', name='user_log'),
    url(r'^report/$',
        'cc.apps.reports.views.report_index', name='report_index'),
    url(r'^remove_bounce/(?P<bounce_id>\d+)/$',
        'cc.apps.reports.views.remove_bounce', name='remove_bounce'),

    # registration
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=UserCreationForm),
        name='accounts_register'),
    url(r'^accounts/login/$',
        'django.contrib.auth.views.login',
        name='auth_login'),
    url(r'^accounts/logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='auth_logout'),
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'password_reset_form': UserPasswordResetForm},
        name='auth_password_reset'),
    url(r'^accounts/invite/$',
        'cc.apps.accounts.views.invite',
        name='accounts_invite'),
    url(r'^accounts/remove_invitation/(?P<invitation_id>\d+)/$',
        'cc.apps.accounts.views.remove_invitation',
        name='remove_invitation'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    ## Hunger- its urls is missing beta_verify_invite
    url(r'^verify/(\w+)/$',
        'hunger.views.verify_invite', name='beta_verify_invite'),
    url(r'hunger', include('hunger.urls')),

    # Sendgrid parse API endpoint
    url(r'^sendgrid_parse/$',
        'cc.apps.main.views.sendgrid_parse', name='sendgrid_parse'),
    #Profile View
    # url(r'^profile_view/$',
    #    'cc.apps.main.views.profile_view', name='profile_view'),
    # django-stripe cc_stripe

    url(r'^payments/a/cancel/$',
        'cc.apps.cc_stripe.views.cancel', name='payments_ajax_cancel'),
    url(r'^payments/a/subscribe/$',
        'cc.apps.cc_stripe.views.subscribe', name='payments_ajax_subscribe'),
    url(r'^payments/subscribe/$',
        login_required(SubscribeView.as_view()), name='payments_subscribe'),
    url(r'^payments/new_subscriber/$',
        login_required(NewSubscriberView.as_view()),
        name='new_payments_subscribe'),
    url(r'^payments/cancel/$',
        login_required(CancelView.as_view()), name='payments_cancel'),
    url(r'^payments/webhook/$',
        'cc.apps.cc_stripe.views.webhook', name='payments_webhook'),


    url(r'^payments/', include('payments.urls')),
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
