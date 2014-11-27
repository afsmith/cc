from django.db import models

from cc.apps.accounts.models import CUser


class Contact(models.Model):
    work_email = models.EmailField(max_length=100)
    work_phone = models.CharField(max_length=100, blank=True)
    work_fax = models.CharField(max_length=100, blank=True)
    work_website = models.CharField(max_length=100, blank=True)
    personal_email = models.EmailField(max_length=100, blank=True)
    home_phone = models.CharField(max_length=100, blank=True)
    mobile_phone = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(CUser)

    class Meta:
        unique_together = ('user', 'work_email')

    def __unicode__(self):
        return self.work_email
