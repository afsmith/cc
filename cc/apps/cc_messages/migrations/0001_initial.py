# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Message'
        db.create_table(u'cc_messages_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=130)),
            ('receivers', self.gf('django.db.models.fields.TextField')()),
            ('cc_me', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('notify_email_opened', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('notify_link_clicked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attachment', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'cc_messages', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Message'
        db.delete_table(u'cc_messages_message')


    models = {
        u'cc_messages.message': {
            'Meta': {'object_name': 'Message'},
            'attachment': ('django.db.models.fields.IntegerField', [], {}),
            'cc_me': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notify_email_opened': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_link_clicked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receivers': ('django.db.models.fields.TextField', [], {}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '130'})
        }
    }

    complete_apps = ['cc_messages']