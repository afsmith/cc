from django.db import models
#from django.utils.translation import ugettext_lazy as _

from cc.apps.accounts.models import CUser


class Bounce(models.Model):
    email = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    reason = models.CharField(max_length=255)
    sender = models.ForeignKey(CUser, null=True, blank=True)
    created_at = models.DateTimeField()

    def __unicode__(self):
        return '{} {}'.format(self.email, self.reason)
