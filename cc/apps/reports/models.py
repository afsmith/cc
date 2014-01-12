from django.db import models
#from django.utils.translation import ugettext_lazy as _

from cc.apps.cc_messages.models import Message


class Bounce(models.Model):
    email = models.CharField(max_length=100)
    reason = models.TextField(null=True, blank=True)
    message = models.ForeignKey(Message, null=True, blank=True)
    event_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} {}'.format(self.email, self.reason)
