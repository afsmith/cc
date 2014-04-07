from django.db import models
from django.contrib.auth import models as auth_models
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
    notify_email_opened = models.BooleanField(_('Notify email is opened'))
    notify_link_clicked = models.BooleanField(_('Notify link is clicked'))
    files = models.ManyToManyField(File, related_name='files')
    key_page = models.IntegerField(_('Key page'), null=True, blank=True)
    link_text = models.CharField(_('Link text'), max_length=150, blank=True)

    owner = models.ForeignKey(CUser, related_name='owner', null=True)
    group = models.ForeignKey(auth_models.Group, null=True)
    expired_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def is_available_for_user(self, user):
        return self.group in user.groups.all() or self.owner == user

    def __unicode__(self):
        return self.subject
