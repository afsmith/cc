from django.conf.urls import patterns, url, include

from django.contrib.auth.decorators import login_required
from .views import (
    CancelView,
    SubscribeView,
    NewSubscriberView,
)

urlpatterns = patterns(
    '',
    url(r'^a/cancel/$',
        'cc.apps.cc_stripe.views.cancel', name='payments_ajax_cancel'),
    url(r'^a/subscribe/$',
        'cc.apps.cc_stripe.views.subscribe', name='payments_ajax_subscribe'),
    url(r'^subscribe/$',
        login_required(SubscribeView.as_view()), name='payments_subscribe'),
    url(r'^new_subscriber/$',
        login_required(NewSubscriberView.as_view()),
        name='new_payments_subscribe'),
    url(r'^cancel/$',
        login_required(CancelView.as_view()), name='payments_cancel'),
    url(r'^webhook/$',
        'cc.apps.cc_stripe.views.webhook', name='payments_webhook'),
    url(r'', include('payments.urls')),
)
