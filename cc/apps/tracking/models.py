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

    def __unicode__(self):
        return 'Page number: %d - Time: %d' % (
            self.page_number, self.total_time
        )