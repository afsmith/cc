from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sessions.models import Session

from cc.apps.cc_messages.models import Message
from cc.apps.accounts.models import CUser


class TrackingEvent(models.Model):
    OPEN_EVENT_TYPE = 'OPEN'
    PAGE_EVENT_TYPE = 'PAGE'

    message = models.ForeignKey(Message)
    participant = models.ForeignKey(CUser)
    session = models.ForeignKey(Session)
    event_type = models.CharField(_('Event type'), max_length=50)
    page_number = models.IntegerField(_('Page number'), null=True)
    total_time = models.BigIntegerField(_('Total time'), default=0)
    client_ip = models.CharField(_('Client IP'), max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s. Event: %s' % (self.message.subject, self.event_type)
