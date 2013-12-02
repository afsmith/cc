# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'File.is_downloadable'
        db.delete_column(u'content_file', 'is_downloadable')

        # Deleting field 'File.duration'
        db.delete_column(u'content_file', 'duration')

        # Deleting field 'File.title'
        db.delete_column(u'content_file', 'title')

        # Deleting field 'File.note'
        db.delete_column(u'content_file', 'note')

        # Deleting field 'File.expires_on'
        db.delete_column(u'content_file', 'expires_on')

        # Deleting field 'File.is_removed'
        db.delete_column(u'content_file', 'is_removed')

        # Deleting field 'File.language'
        db.delete_column(u'content_file', 'language')

        # Deleting field 'File.delete_expired'
        db.delete_column(u'content_file', 'delete_expired')


    def backwards(self, orm):
        # Adding field 'File.is_downloadable'
        db.add_column(u'content_file', 'is_downloadable',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'File.duration'
        db.add_column(u'content_file', 'duration',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'File.title'
        db.add_column(u'content_file', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=150),
                      keep_default=False)

        # Adding field 'File.note'
        db.add_column(u'content_file', 'note',
                      self.gf('django.db.models.fields.CharField')(max_length=400, null=True),
                      keep_default=False)

        # Adding field 'File.expires_on'
        db.add_column(u'content_file', 'expires_on',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'File.is_removed'
        db.add_column(u'content_file', 'is_removed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'File.language'
        db.add_column(u'content_file', 'language',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=7),
                      keep_default=False)

        # Adding field 'File.delete_expired'
        db.add_column(u'content_file', 'delete_expired',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


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
        u'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'4zWke26pgtgf2asehxFRgp'", 'unique': 'True', 'max_length': '22'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'0XzWY'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'4Ke2v'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'iJCll'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'vgYDu'", 'max_length': '5'}),
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

    complete_apps = ['content']