from django.db import models
from django.utils.translation import ugettext_lazy as _

from cc.apps.accounts.models import CUser


class Message(models.Model):
    '''
    Message model for saving the original message of senders
    '''
    subject = models.CharField(_('Subject'), max_length=130)
    receivers = models.ManyToManyField(CUser, related_name='receivers')
    cc_me = models.BooleanField(_('CC me'))
    message = models.TextField(_('Message'))
    notify_email_opened = models.BooleanField(_('Notify email opened'))
    notify_link_clicked = models.BooleanField(_('Notify link clicked'))
    attachment = models.IntegerField(_('Attachment'))
    owner = models.ForeignKey(CUser, related_name='owner', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.subject + self.message
