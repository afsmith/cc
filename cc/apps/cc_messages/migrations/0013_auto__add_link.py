# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Link'
        db.create_table(u'cc_messages_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('original_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('converted_key', self.gf('django.db.models.fields.CharField')(default='mfOzq3fRzlrLfnJkLMQdOF', unique=True, max_length=100)),
        ))
        db.send_create_signal(u'cc_messages', ['Link'])


    def backwards(self, orm):
        # Deleting model 'Link'
        db.delete_table(u'cc_messages_link')


    models = {
        u'accounts.cuser': {
            'Meta': {'object_name': 'CUser'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
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
        u'cc_messages.link': {
            'Meta': {'object_name': 'Link'},
            'converted_key': ('django.db.models.fields.CharField', [], {'default': "'P3hdyTT7CKk62SFik2qdau'", 'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'cc_messages.message': {
            'Meta': {'object_name': 'Message'},
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cc_me': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'files'", 'symmetrical': 'False', 'to': u"orm['content.File']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'null': 'True', 'to': u"orm['accounts.CUser']"}),
            'receivers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'receivers'", 'symmetrical': 'False', 'to': u"orm['accounts.CUser']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '130'})
        },
        u'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'Kgr5Y7SAFfFFChSrqxAvur'", 'unique': 'True', 'max_length': '22'}),
            'link_text': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'8an8q'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'eZlBd'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'xO4Tb'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'oJeNA'", 'max_length': '5'}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cc_messages']