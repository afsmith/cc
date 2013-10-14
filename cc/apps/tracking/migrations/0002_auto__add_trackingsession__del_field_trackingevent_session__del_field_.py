# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrackingSession'
        db.create_table(u'tracking_trackingsession', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cc_messages.Message'])),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.CUser'])),
            ('client_ip', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tracking', ['TrackingSession'])

        # Deleting field 'TrackingEvent.session'
        db.delete_column(u'tracking_trackingevent', 'session_id')

        # Deleting field 'TrackingEvent.client_ip'
        db.delete_column(u'tracking_trackingevent', 'client_ip')

        # Deleting field 'TrackingEvent.event_type'
        db.delete_column(u'tracking_trackingevent', 'event_type')

        # Deleting field 'TrackingEvent.participant'
        db.delete_column(u'tracking_trackingevent', 'participant_id')

        # Deleting field 'TrackingEvent.created_at'
        db.delete_column(u'tracking_trackingevent', 'created_at')

        # Deleting field 'TrackingEvent.message'
        db.delete_column(u'tracking_trackingevent', 'message_id')

        # Adding field 'TrackingEvent.tracking_session'
        db.add_column(u'tracking_trackingevent', 'tracking_session',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tracking.TrackingSession'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TrackingSession'
        db.delete_table(u'tracking_trackingsession')

        # Adding field 'TrackingEvent.session'
        db.add_column(u'tracking_trackingevent', 'session',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sessions.Session']),
                      keep_default=False)

        # Adding field 'TrackingEvent.client_ip'
        db.add_column(u'tracking_trackingevent', 'client_ip',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True),
                      keep_default=False)

        # Adding field 'TrackingEvent.event_type'
        db.add_column(u'tracking_trackingevent', 'event_type',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'TrackingEvent.participant'
        db.add_column(u'tracking_trackingevent', 'participant',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['accounts.CUser']),
                      keep_default=False)

        # Adding field 'TrackingEvent.created_at'
        db.add_column(u'tracking_trackingevent', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2013, 10, 15, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'TrackingEvent.message'
        db.add_column(u'tracking_trackingevent', 'message',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['cc_messages.Message']),
                      keep_default=False)

        # Deleting field 'TrackingEvent.tracking_session'
        db.delete_column(u'tracking_trackingevent', 'tracking_session_id')


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
        u'cc_messages.message': {
            'Meta': {'object_name': 'Message'},
            'cc_me': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'files'", 'symmetrical': 'False', 'to': u"orm['content.File']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notify_email_opened': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_link_clicked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'null': 'True', 'to': u"orm['accounts.CUser']"}),
            'pricing_page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'receivers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'receivers'", 'symmetrical': 'False', 'to': u"orm['accounts.CUser']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '130'})
        },
        u'content.file': {
            'Meta': {'ordering': "('created_on',)", 'object_name': 'File'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delete_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'expires_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_downloadable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'VSz2dLvLykICGdzfG9Buc'", 'unique': 'True', 'max_length': '22'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True'}),
            'orig_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']", 'null': 'True'}),
            'pages_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'subkey_conv': ('django.db.models.fields.CharField', [], {'default': "'MEfZZ'", 'max_length': '5'}),
            'subkey_orig': ('django.db.models.fields.CharField', [], {'default': "'Tkgbm'", 'max_length': '5'}),
            'subkey_preview': ('django.db.models.fields.CharField', [], {'default': "'SrEYJ'", 'max_length': '5'}),
            'subkey_thumbnail': ('django.db.models.fields.CharField', [], {'default': "'PJenT'", 'max_length': '5'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
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
        u'tracking.trackingevent': {
            'Meta': {'object_name': 'TrackingEvent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'total_time': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'tracking_session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tracking.TrackingSession']", 'null': 'True'})
        },
        u'tracking.trackingsession': {
            'Meta': {'object_name': 'TrackingSession'},
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cc_messages.Message']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.CUser']"})
        }
    }

    complete_apps = ['tracking']