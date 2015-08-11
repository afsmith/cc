# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    no_dry_run = True
    def forwards(self, orm):
        # Adding field 'TrackingSession.file_index'
        db.add_column(u'tracking_trackingsession', 'file_index',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


        # Changing field 'TrackingSession.tracking_log'
        db.alter_column(u'tracking_trackingsession', 'tracking_log_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracking.TrackingLog'], null=True))
        # Adding field 'TrackingLog.file_index'
        db.add_column(u'tracking_trackinglog', 'file_index',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        for log in orm.TrackingLog.objects.all():
            if log.action == orm.TrackingLog.OPEN_EMAIL_ACTION:
                log.file_index = 0
                log.save()


    def backwards(self, orm):
        # Deleting field 'TrackingSession.file_index'
        db.delete_column(u'tracking_trackingsession', 'file_index')


        # Changing field 'TrackingSession.tracking_log'
        db.alter_column(u'tracking_trackingsession', 'tracking_log_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['tracking.TrackingLog']))
        # Deleting field 'TrackingLog.file_index'
        db.delete_column(u'tracking_trackinglog', 'file_index')


    models = {
        u'accounts.cuser': {
            'Meta': {'object_name': 'CUser'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'signature': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'user_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'cc_messages.message': {
            'Meta': {'object_name': 'Message'},
            'cc_me': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'files'", 'symmetrical': 'False', 'to': u"orm['content.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notify_email_opened': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_link_clicked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'null': 'True', 'to': u"orm['accounts.CUser']"}),
            'receivers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'receivers'", 'symmetrical': 'False', 'to': u"orm['accounts.CUser']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '130'})
        },
        u'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'MWWhR6ymsncbqNITbxhPa1'", 'unique': 'True', 'max_length': '22'}),
            'link_text': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'GKaxS'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'t15th'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'ezETk'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'HioX9'", 'max_length': '5'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tracking.closeddeal': {
            'Meta': {'object_name': 'ClosedDeal'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cc_messages.Message']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
        },
        u'tracking.trackingevent': {
            'Meta': {'object_name': 'TrackingEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'page_view': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_time': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'tracking_session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracking.TrackingSession']", 'null': 'True'})
        },
        u'tracking.trackinglog': {
            'Meta': {'object_name': 'TrackingLog'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_index': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cc_messages.Message']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"}),
            'revision': ('django.db.models.fields.IntegerField', [], {})
        },
        u'tracking.trackingsession': {
            'Meta': {'object_name': 'TrackingSession'},
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'file_index': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cc_messages.Message']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"}),
            'tracking_log': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracking.TrackingLog']", 'null': 'True'})
        }
    }

    complete_apps = ['tracking']
