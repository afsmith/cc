from django.db import models
from django.db.models import Q

from cc.apps.accounts.models import CUser

import operator


class ContactManager(models.Manager):
    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

    def search(self, search_terms):
        if not search_terms:
            return self.none()

        terms = [term.strip() for term in search_terms.split()]
        q_objects = []

        for term in terms:
            q_objects.append(Q(work_email__icontains=term))
            q_objects.append(Q(first_name__icontains=term))
            q_objects.append(Q(last_name__icontains=term))
            q_objects.append(Q(company__icontains=term))

        # Start with a bare QuerySet
        qs = self.get_query_set()

        # Use operator's or_ to string together all of your Q objects.
        return qs.filter(reduce(operator.or_, q_objects)).distinct()


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
    crmContactId = models.IntegerField(default=0)

    objects = ContactManager()

    class Meta:
        unique_together = ('user', 'work_email','crmContactId')

    def __unicode__(self):
        return self.work_email
