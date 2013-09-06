from django.db import models

#from accounts.models import WhamUser


class Message(models.Model):
    subject = models.CharField(max_length=130)
    description = models.TextField(blank=True)
    hashed_id = models.CharField(max_length=20)
    content = models.TextField()
    #added_by = models.ForeignKey(WhamUser)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
