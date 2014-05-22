from django.db import models
from django.utils.translation import ugettext_lazy as _

from cc.apps.accounts.models import CUser
from cc.apps.content.models import File


class Message(models.Model):
    '''
    Message model for saving the original message of senders
    '''
    subject = models.CharField(_('Subject'), max_length=130)
    receivers = models.ManyToManyField(CUser, related_name='receivers')
    cc_me = models.BooleanField(_('Send me a copy'))
    message = models.TextField(_('Message'))
    allow_download = models.BooleanField(_('Allow download'))
    files = models.ManyToManyField(File, related_name='files')
    owner = models.ForeignKey(CUser, related_name='owner', null=True)
    expired_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def is_available_for_user(self, user):
        return user in self.receivers.all() or self.owner == user

    def __unicode__(self):
        return self.subject
