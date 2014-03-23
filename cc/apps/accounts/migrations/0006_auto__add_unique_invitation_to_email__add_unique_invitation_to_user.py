# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'Invitation', fields ['to_email']
        db.create_unique(u'accounts_invitation', ['to_email'])

        # Adding unique constraint on 'Invitation', fields ['to_user']
        db.create_unique(u'accounts_invitation', ['to_user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Invitation', fields ['to_user']
        db.delete_unique(u'accounts_invitation', ['to_user_id'])

        # Removing unique constraint on 'Invitation', fields ['to_email']
        db.delete_unique(u'accounts_invitation', ['to_email'])


    models = {
        u'accounts.billingaddress': {
            'Meta': {'object_name': 'BillingAddress'},
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'address_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'address_zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
        },
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
        u'accounts.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'fd9G6AZHRBNjOjd1OBF100vtV5vYvW'", 'max_length': '30'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites_sent'", 'to': u"orm['accounts.CUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'SENT'", 'max_length': '30'}),
            'to_email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites_receive'", 'unique': 'True', 'null': 'True', 'to': u"orm['accounts.CUser']"})
        },
        u'accounts.oneclicklinktoken': {
            'Meta': {'object_name': 'OneClickLinkToken'},
            'allow_login': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'qOKi0ddgAtXWYq9FjMhDaz76PyXN6g'", 'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']