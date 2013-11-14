from django.db import models
from django.utils.translation import ugettext_lazy as _

from cc.apps.cc_messages.models import Message
from cc.apps.accounts.models import CUser


class TrackingSession(models.Model):
    message = models.ForeignKey(Message)
    participant = models.ForeignKey(CUser)
    client_ip = models.CharField(_('Client IP'), max_length=50, null=True)
    device = models.CharField(_('Device'), max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message.subject


class TrackingEvent(models.Model):
    tracking_session = models.ForeignKey(TrackingSession, null=True)
    page_number = models.IntegerField(_('Page number'), null=True)
    total_time = models.BigIntegerField(_('Total time'), default=0)
    page_view = models.IntegerField(_('Page view'), default=0)

    def __unicode__(self):
        return 'Page number: {} - Time: {} - PV: {}'.format(
            self.page_number, self.total_time, self.page_view
        )


class ClosedDeal(models.Model):
    message = models.ForeignKey(Message)
    participant = models.ForeignKey(CUser)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message.subject


class TrackingLog(models.Model):
    OPEN_EMAIL_ACTION = 'OPEN_EMAIL'
    CLICK_LINK_ACTION = 'CLICK_LINK'

    message = models.ForeignKey(Message)
    participant = models.ForeignKey(CUser)
    action = models.CharField(_('Action'), max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message.subject
